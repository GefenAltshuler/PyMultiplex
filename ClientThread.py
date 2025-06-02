import logging
import socket
import struct
import sys
import threading
import random
from typing import Tuple, List, Dict
from consts import MAX_CHANNEL_CLIENTS, MAX_CHANNELS, HEADERS_SIZE, MIN_CHANNELS, DEFAULT_BIND_ADDRESS, \
    MAX_PIPE_CLIENTS, BUFFER_SIZE

from ChannelSocket import ChannelSocket
from Exceptions import MaxChannelsReached, ProtocolInitializationFailed
from Message import MessageCode

import logging
import socket
import struct
from threading import Thread
from typing import Dict

from ChannelSocket import ChannelSocket
from Message import Message
from consts import HEADERS_SIZE


class ClientThread(Thread):
    def __init__(self, sock: ChannelSocket):
        self._sock: ChannelSocket = sock
        self._channels: Dict[int, ChannelSocket] = {}
        self.
        super().__init__()

    def _info(self, log: str):
        logging.info(f"{self.__class__.__name__} [{self.ident}]: {log}")

    def _debug(self, log: str):
        logging.debug(f"{self.__class__.__name__} [{self.ident}]: {log}")

    def _recv_message(self):
        headers = self._sock.recv(HEADERS_SIZE)
        channel, code, length = struct.unpack('!BBI', headers)
        data = self._sock.recv(length)
        self._debug(f'Data received: {channel}|{code}|{length}|{data}')

        return Message(channel, code, data)

    def _send_message(self, message: Message):
        return self._sock.sendall(message.to_bytes())

    def _get_channel_number(self):
        channel = random.randint(MIN_CHANNELS, MAX_CHANNELS)
        if len(self._channels) >= (MAX_CHANNELS-MIN_CHANNELS):
            raise MaxChannelsReached

        if channel in self._channels.keys():
            return self._get_channel_number()

        return channel

    def _pipe_closed_channel(self, channel: int):
        close_message = Message(channel, MessageCode.close)
        self._send_message(close_message)
        self._channels.pop(channel)

    def _remote_closed_channel(self, channel: int):
        self._channels.pop(channel)

    def _pipe_to_channel(self, channel: int, pipe_socket: socket.socket):
        while True: # todo: add support for closing pipe from other thread

            # pipe socket closed
            pipe_data = pipe_socket.recv(BUFFER_SIZE)
            if not pipe_data:
                self._pipe_closed_channel(channel)
                pipe_socket.close()
                sys.exit()

            # normal data transfer
            data_message = Message(channel, MessageCode.data, pipe_data)
            self._send_message(data_message)

    def _channel_to_pipe(self, channel: int, pipe_socket: socket.socket):
        while True:  # todo: add support for closing pipe from other thread
            message = self._recv_message()
            if message.code == MessageCode.data:
                pipe_socket.sendall(message.data)
            elif message.code == MessageCode.close:
                pipe_socket.close()
                self._remote_closed_channel(channel)
                sys.exit()


            # # pipe socket closed
            # pipe_data = pipe_socket.recv(BUFFER_SIZE)
            # if not pipe_data:
            #     self._close_channel(channel)
            #     pipe_socket.close()
            #     sys.exit()
            #
            # # normal data transfer
            # data_message = Message(channel, MessageCode.data, pipe_data)
            # self._send_message(data_message)

    def start(self):
        channels: Dict[int, ChannelSocket] = {}

        message = self._recv_message()
        if message.code != MessageCode.bind:
            raise ProtocolInitializationFailed

        pipe_port = struct.unpack('!H', message.data)[0]
        pipe_socket = socket.socket()
        bind_address = (DEFAULT_BIND_ADDRESS, pipe_port)

        pipe_socket.bind(bind_address)
        pipe_socket.listen(MAX_PIPE_CLIENTS)

        self._info(f"Listening on {bind_address}")

        while True:
            pipe_client, pipe_client_address = pipe_socket.accept()
            self._info(f"Connected by {pipe_client_address}")

            channel = self._get_channel_number()
            open_channel_message = Message(channel, MessageCode.open, message.data)
            self._send_message(open_channel_message) # now client init connection to target server


        # while True:
        #     # accept new client
        #     client_socket, client_address = server_socket.accept()
        #     logging.info(f"Connected by {client_address}")
        #
        # channel = get_channel_number(channels)
        # channel_socket = ChannelSocket(client_socket)
        # channels[channel] = channel_socket

        super().start()
