import socket
import struct
from typing import Tuple

from PyMultiplex.utils.Logger import Logger
from PyMultiplex.Channel.Message import Message, MessageCode
from PyMultiplex.Threads.MultiplexClientThread import MultiplexClientThread
from PyMultiplex.utils.consts import DEFAULT_CHANNEL


class MultiplexClient:
    def __init__(self, server_address: Tuple[str, int], target_address: Tuple[str, int], remote_forward_port: int):
        self._multiplex_socket = socket.socket()
        self._server_address = server_address
        self._target_address = target_address
        self._remote_forward_port = remote_forward_port
        self._logger = Logger(self)
        self.ident = id(self)


    def start(self):
        """
        request new bind, then assign new channel for both sides
        """
        self._logger.info(f"connecting to {self._server_address}")
        self._multiplex_socket.connect(self._server_address)

        # make the remote server start listening
        forward_listen_port = struct.pack('!H', self._remote_forward_port)
        bind_message = Message(DEFAULT_CHANNEL, MessageCode.bind, forward_listen_port).to_bytes()
        self._multiplex_socket.sendall(bind_message)

        # wait for messages from server
        multiplex_thread = MultiplexClientThread(self._target_address, self._multiplex_socket)
        multiplex_thread.start()

