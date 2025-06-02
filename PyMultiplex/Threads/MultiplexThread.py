import random
import socket
import struct
import threading
from abc import ABC
from typing import Dict, Union
import binascii

from PyMultiplex.Channel.Exceptions import MaxChannelsReached, RemoteSocketClosed, UnknownProtocolMessage
from PyMultiplex.Channel.Message import Message
from PyMultiplex.Channel.Message import MessageCode
from PyMultiplex.Channel.Socket import ChannelSocket
from PyMultiplex.utils.Logger import Logger
from PyMultiplex.utils.consts import MAX_CHANNELS, MIN_CHANNELS, BUFFER_SIZE, HEADERS_SIZE


class MultiplexThread(ABC):
    def __init__(self, remote_sock: socket.socket):
        self._remote_sock: socket.socket = remote_sock
        self._channels: Dict[int, ChannelSocket] = {}
        self.ident = id(self)
        self._logger = Logger(self)

    def _get_pipe_socket(self) -> socket.socket:
        raise NotImplementedError('unsupported')

    def _forward_listen(self, pipe_port: int) -> None:
        raise NotImplementedError('unsupported')

    def _recv_message(self):
        headers = self._remote_sock.recv(HEADERS_SIZE)
        if not headers: raise RemoteSocketClosed
        try:
            channel, code, length = struct.unpack('!BBI', headers)
            data = self._remote_sock.recv(length)
            self._logger.debug(f'Data received: {channel}|{code}|{length}|{binascii.hexlify(data)}')
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
        channel_socket = ChannelSocket(channel_id, self._remote_sock)
        self._channels[channel_id] = channel_socket
        MultiplexThread._open_pipe(channel_socket, self._get_pipe_socket())

    @staticmethod
    def _open_pipe(channel_socket: ChannelSocket, pipe_socket: socket.socket):
        # transfer data in both directions
        threading.Thread(target=MultiplexThread._pipe, args=(pipe_socket, channel_socket)).start()
        threading.Thread(target=MultiplexThread._pipe, args=(channel_socket, pipe_socket)).start()

    def _close_channel(self, channel_id: int):
        self._logger.debug(f'Closing channel {channel_id}')
        channel = self._channels.pop(channel_id)
        channel.is_open = False

    def listen_for_messages(self):
        """
         listen for messages from all channels and feed the appropriate ChannelSocket
        """
        while True:
            try:
                message = self._recv_message()
                if message.code == MessageCode.bind:
                    pipe_port = struct.unpack('!H', message.data)[0]
                    threading.Thread(target=self._forward_listen, args=(pipe_port,)).start()
                if message.code == MessageCode.open:
                    self._open_new_channel(message.channel)
                elif message.code == MessageCode.close:
                    self._channels[message.channel].put(b'')
                    self._close_channel(message.channel)
                elif message.code == MessageCode.data:
                    self._channels[message.channel].put(message.data)


            except RemoteSocketClosed:
                self._logger.error(f"Remote socket closed, closing all channels")
                del self._channels
                break
            except UnknownProtocolMessage as e:
                self._logger.error(str(e))

    def start(self):
        """
        handshake with the client, then assign new channel for both sides
        """
        self.listen_for_messages()

    @staticmethod
    def _pipe(s1: Union[ChannelSocket, socket.socket], s2: Union[ChannelSocket, socket.socket]):

        while True:  # todo: add support for closing pipe from other thread (maybe there is no need?)
            try:
                data = s1.recv(BUFFER_SIZE)
                if not data: raise ConnectionError
            except ConnectionError as e:
                Logger.inner_debug(f"socket closed {str(e)}", MultiplexThread)
                s1.close()
                s2.close()
                break
            else:
                s2.sendall(data)
