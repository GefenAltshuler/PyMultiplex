import socket
import struct
import threading
from typing import Tuple

from utils.Logger import Logger
from Channel.Message import Message, MessageCode
from Threads.MultiplexClientThread import MultiplexClientThread
from utils.consts import DEFAULT_CHANNEL

FORWARD_LISTEN_PORT = 7190
TARGET_SERVER = ('209.38.142.101', 22)


class MultiplexClient:
    def __init__(self, server_address: Tuple[str, int]):
        self._multiplex_socket = socket.socket()
        self._server_address = server_address
        self._logger = Logger(self)
        self.ident = id(self)


    def start(self):
        """
        request new bind, then assign new channel for both sides
        """
        self._logger.info(f"connecting to {self._server_address}")
        self._multiplex_socket.connect(self._server_address)

        # make the remote server start listening
        forward_listen_port = struct.pack('!H', FORWARD_LISTEN_PORT)
        bind_message = Message(DEFAULT_CHANNEL, MessageCode.bind, forward_listen_port).to_bytes()
        self._multiplex_socket.sendall(bind_message)

        # wait for messages from server
        multiplex_thread = MultiplexClientThread(TARGET_SERVER, self._multiplex_socket)
        multiplex_thread.start()

