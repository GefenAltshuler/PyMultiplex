import logging
import socket
import struct
import threading
from typing import Tuple

from Exceptions import ProtocolInitializationFailed
from Message import Message, MessageCode
from MultiplexThread import MultiplexThread
from Logger import Logger
from consts import MAX_CLIENTS, DEFAULT_BIND_ADDRESS


class MultiplexServer:
    def __init__(self, listen_address: Tuple[str, int]):
        self._multiplex_socket = socket.socket()
        self._multiplex_socket.bind(listen_address)
        self._max_clients = MAX_CLIENTS
        self._logger = Logger(self)
        self.ident = id(self)

    def _start(self, remote_socket: socket.socket):
        """
        handshake with the client, then assign new channel for both sides
        """
        message = Message.recv(remote_socket)
        if message.code != MessageCode.bind:
            raise ProtocolInitializationFailed

        # get port to listen
        pipe_port = struct.unpack('!H', message.data)[0]
        pipe_listen_socket = socket.socket()
        bind_address = (DEFAULT_BIND_ADDRESS, pipe_port)

        # start listen for incoming connections
        pipe_listen_socket.bind(bind_address)
        pipe_listen_socket.listen(MAX_CLIENTS)
        self._logger.info(f"Listening on {bind_address}")

        while True:
            pipe_socket, pipe_client_address = pipe_listen_socket.accept()
            self._logger.info(f"Connected by {pipe_client_address}")

            # create new channel
            multiplex_thread = MultiplexThread(remote_socket, pipe_socket)
            channel_socket = multiplex_thread.init_new_channel()

            threading.Thread(target=multiplex_thread.start).start()

    def start(self):
        self._multiplex_socket.listen(self._max_clients)
        self._logger.info(f"Listening on {self._multiplex_socket.getsockname()}")

        while True:
            client_socket, client_address = self._multiplex_socket.accept()
            self._logger.info(f"Connected by {client_address}")
            threading.Thread(target=self._start, args=(client_socket, )).start()
