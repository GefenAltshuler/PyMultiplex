import random
import socket
import struct
import threading
from typing import Dict, Union

from Channel.Socket import ChannelSocket
from Channel.Exceptions import MaxChannelsReached, RemoteSocketClosed, UnknownProtocolMessage
from Channel.Message import Message
from Channel.Message import MessageCode
from utils.consts import MAX_CHANNELS, MIN_CHANNELS, BUFFER_SIZE, HEADERS_SIZE
from utils.Logger import Logger
from abc import abstractmethod, ABC

class MultiplexThread(ABC):
    def __init__(self, remote_sock: socket.socket, pipe_socket: socket.socket):
        self._remote_sock: socket.socket = remote_sock
        self._channels: Dict[int, ChannelSocket] = {}
        self.ident = id(self)
        self._logger = Logger(self)

    @abstractmethod
    def _get_pipe_socket(self) -> socket.socket:
        pass

    def _recv_message(self):
        headers = self._remote_sock.recv(HEADERS_SIZE)
        if not headers: raise RemoteSocketClosed
        try:
            channel, code, length = struct.unpack('!BBI', headers)
            data = self._remote_sock.recv(length)
            self._logger.debug(f'Data received: {channel}|{code}|{length}|{data}')
        except struct.error:
            raise UnknownProtocolMessage(headers)

        return Message(channel, code, data)

    def _send_message(self, message: Message):
        return self._remote_sock.sendall(message.to_bytes())

    def get_new_channel_id(self):
        channel = random.randint(MIN_CHANNELS, MAX_CHANNELS)
        if len(self._channels) >= (MAX_CHANNELS - MIN_CHANNELS):
            raise MaxChannelsReached

        if channel in self._channels.keys():
            return self.get_new_channel_id()

        return channel


    def _open_new_channel(self, channel_id: int):
        # create new channel socket
        channel_socket = ChannelSocket(channel_id)
        self._channels[channel_id] = ChannelSocket(channel_id)
        self._open_pipe(channel_socket)

    def _open_pipe(self, channel_socket: ChannelSocket):
        # transfer data in both directions
        threading.Thread(target=MultiplexThread._pipe, args=(self._get_pipe_socket(), channel_socket)).start()
        threading.Thread(target=MultiplexThread._pipe, args=(channel_socket, self._get_pipe_socket())).start()

    def _close_channel(self, channel_id: int):
        channel = self._channels.pop(channel_id)
        channel.is_open = False

    def _check_for_closed_channels(self):
        for channel in self._channels.values():
            if not channel.is_open:
                closing_message = channel.get_closing_message()
                self._send_message(closing_message)
                self._close_channel(closing_message.channel)

    def start(self):
        """
         listen for messages from all channels and feed the appropriate ChannelSocket
        """
        while True:
            try:
                message = self._recv_message()
                if message.code == MessageCode.open:
                    self._open_new_channel(message.channel)
                elif message.code == MessageCode.close:
                    self._channels[message.channel].put(b'')
                    self._close_channel(message.channel)
                elif message.code == MessageCode.data:
                    self._channels[message.channel].put(message.data)
                self._check_for_closed_channels()

            except RemoteSocketClosed:
                self._logger.error(f"Remote socket closed, closing all channels")
                del self._channels
                break
            except UnknownProtocolMessage as e:
                self._logger.error(str(e))

    @staticmethod
    def _pipe(s1: Union[ChannelSocket, socket.socket], s2: Union[ChannelSocket, socket.socket]):
        while True:  # todo: add support for closing pipe from other thread (maybe there is no need?)
            data = s1.recv(BUFFER_SIZE)
            if not data:
                s1.close()
                s2.close()
                break
            else:
                s2.send(data)
