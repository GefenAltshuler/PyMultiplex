import threading
import logging
import random
import socket
import struct
import threading
from typing import Dict, Union

from ChannelSocket import ChannelSocket
from Exceptions import MaxChannelsReached, ProtocolInitializationFailed, RemoteSocketClosed, UnknownProtocolMessage
from Message import Message
from Message import MessageCode
from consts import MAX_CHANNELS, MIN_CHANNELS, DEFAULT_BIND_ADDRESS, \
    MAX_CLIENTS, BUFFER_SIZE, HEADERS_SIZE


class MultiplexThread:
    def __init__(self, remote_sock: socket.socket):
        self._remote_sock: socket.socket = remote_sock
        self._channels: Dict[int, ChannelSocket] = {}
        self.ident = id(self)

    def _error(self, log: str):
        logging.error(f"{self.__class__.__name__} [{self.ident}]: {log}")

    def _info(self, log: str):
        logging.info(f"{self.__class__.__name__} [{self.ident}]: {log}")

    def _debug(self, log: str):
        logging.debug(f"{self.__class__.__name__} [{self.ident}]: {log}")

    def _recv_message(self):
        headers = self._remote_sock.recv(HEADERS_SIZE)
        if not headers: raise RemoteSocketClosed
        try:
            channel, code, length = struct.unpack('!BBI', headers)
            data = self._remote_sock.recv(length)
            self._debug(f'Data received: {channel}|{code}|{length}|{data}')
        except struct.error:
            raise UnknownProtocolMessage(headers)

        return Message(channel, code, data)

    def _send_message(self, message: Message):
        return self._remote_sock.sendall(message.to_bytes())

    def _get_channel_id(self):
        channel = random.randint(MIN_CHANNELS, MAX_CHANNELS)
        if len(self._channels) >= (MAX_CHANNELS - MIN_CHANNELS):
            raise MaxChannelsReached

        if channel in self._channels.keys():
            return self._get_channel_id()

        return channel

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
        message = self._recv_message()
        if message.code != MessageCode.bind:
            raise ProtocolInitializationFailed

        # get port to listen
        pipe_port = struct.unpack('!H', message.data)[0]
        pipe_socket = socket.socket()
        bind_address = (DEFAULT_BIND_ADDRESS, pipe_port)

        # start listen for incoming connections
        pipe_socket.bind(bind_address)
        pipe_socket.listen(MAX_CLIENTS)
        self._info(f"Listening on {bind_address}")
        pipe_client, pipe_client_address = pipe_socket.accept()
        self._info(f"Connected by {pipe_client_address}")

        # assign new channel
        channel_id = self._get_channel_id()
        self._channels[channel_id] = ChannelSocket(channel_id)
        open_channel_message = Message(channel_id, MessageCode.open, message.data)
        self._send_message(open_channel_message)

        # transfer data in both directions
        threading.Thread(target=MultiplexThread._pipe, args=(self._remote_sock, pipe_socket)).start()
        threading.Thread(target=MultiplexThread._pipe, args=(pipe_socket, self._remote_sock)).start()

        # listen for messages from all channels and feed the appropriate ChannelSocket
        while True:
            try:
                message = self._recv_message()
                if message.code == MessageCode.close:
                    self._channels[message.channel].put(b'')
                    self._close_channel(message.channel)
                    continue
                self._channels[message.channel].put(message.data)
                self._check_for_closed_channels()
            except RemoteSocketClosed:
                self._error(f"Remote socket closed, closing all channels")
                del self._channels
                break
            except UnknownProtocolMessage as e:
                self._error(str(e))

    @staticmethod
    def _pipe(s1: Union[ChannelSocket, socket.socket], s2: Union[ChannelSocket, socket.socket]):
        while True:  # todo: add support for closing pipe from other thread
            data = s1.recv(BUFFER_SIZE)
            if not data:
                s1.close()
                s2.close()
                break
            else:
                s2.send(data)
