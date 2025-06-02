import logging
import socket
import struct
import threading
import random
from typing import Tuple, List, Dict
from consts import MAX_CHANNEL_CLIENTS, MAX_CHANNELS, HEADERS_SIZE, MIN_CHANNELS

from ChannelSocket import ChannelSocket
from Exceptions import MaxChannelsReached
from Message import MessageCode

class ChannelServer:
    def __init__(self, channel_listen_address: Tuple[str, int], max_clients: int = MAX_CHANNEL_CLIENTS):
        self._channel_socket = socket.socket()
        self._channel_socket.bind(channel_listen_address)
        self._max_clients = max_clients
        self._client_threads: List[threading.Thread] = []
        self._should_continue = True

    def stop(self):
        self._should_continue = False

    def _log(self, log: str):
        logging.info(f"{self.__class__.__name__}: {log}")

    def recv_message(self, client_socket: socket.socket):
        headers = client_socket.recv(HEADERS_SIZE)
        channel, code, length = struct.unpack('!BBI', headers)
        data = client_socket.recv(length)
        self._log(f'Data received: {channel}|{code}|{length}|{data}')
        handle_message(channel, code, data, client_socket)

    def _client_thread(self, client_socket):
        channels: Dict[int, ChannelSocket] = {}

        channel = ChannelServer.get_channel_number(channels)
        channel_socket = ChannelSocket(client_socket)
        channels[channel] = channel_socket

        #
        # # open new channel
        # channel = get_channel_number(channels)
        # queue = socket.socketpair()
        # channels[channel] = (queue, client_socket)
        #
        # send_greeting_channel(client_socket, channel)
        #
        # message = build_message(channel, Message.open)
        # client_socket.send(message)
        #
        # t = threading.Thread(target=read_messages, args=(client_socket,))
        # t.start()

    def listen(self):
        self._channel_socket.listen(self._max_clients)
        self._log(f"Listening on {self._channel_socket.getsockname()}")

        while self._should_continue:
            client_socket, client_address = self._channel_socket.accept()
            self._log(f"Connected by {client_address}")

            t = threading.Thread(target=self._client_thread, args=(client_socket,))
            self._client_threads.append(t)
            t.start()

