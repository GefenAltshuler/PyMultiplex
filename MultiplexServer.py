import logging
import socket
import threading
from typing import Tuple

from MultiplexThread import MultiplexThread
from consts import MAX_CLIENTS


class MultiplexServer:
    def __init__(self, listen_address: Tuple[str, int]):
        self._channel_socket = socket.socket()
        self._channel_socket.bind(listen_address)
        self._max_clients = MAX_CLIENTS

    def _info(self, log: str):
        logging.info(f"{self.__class__.__name__}: {log}")

    def _debug(self, log: str):
        logging.debug(f"{self.__class__.__name__}: {log}")

    def start(self):
        self._channel_socket.listen(self._max_clients)
        self._info(f"Listening on {self._channel_socket.getsockname()}")

        while True:
            client_socket, client_address = self._channel_socket.accept()
            self._info(f"Connected by {client_address}")
            client_thread = MultiplexThread(client_socket)
            threading.Thread(target=client_thread.start).start()
