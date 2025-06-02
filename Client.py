import socket
import socket
import struct
import threading
from typing import Tuple

from Logger import Logger
from Message import Message, MessageCode
from MultiplexThread import MultiplexThread
from consts import DEFAULT_CHANNEL

FORWARD_LISTEN_PORT = 7190
TARGET_SERVER = ('209.38.142.101', 22)


class MultiplexClient:
    def __init__(self, server_address: Tuple[str, int]):
        self._multiplex_socket = socket.socket()
        self._server_address = server_address
        self._logger = Logger(self)
        self.ident = id(self)

    @staticmethod
    def connect_to_target_server():
        sock = socket.socket()
        sock.connect(TARGET_SERVER)

        return sock

    def _start(self, remote_socket: socket.socket):
        """
        request new bind, then assign new channel for both sides
        """
        # make the remote server start listening
        forward_listen_port = struct.pack('!H', FORWARD_LISTEN_PORT)
        bind_message = Message(DEFAULT_CHANNEL, MessageCode.bind, forward_listen_port).to_bytes()
        remote_socket.sendall(bind_message)

        # connect to target socket
        pipe_socket = MultiplexClient.connect_to_target_server()

        # wait for messages from server
        multiplex_thread = MultiplexThread(remote_socket, pipe_socket)
        threading.Thread(target=multiplex_thread.start).start()

    def start(self):
        self._logger.info(f"connecting to {self._server_address}")
        self._multiplex_socket.connect(self._server_address)


        threading.Thread(target=self._start, args=(client_socket,)).start()
