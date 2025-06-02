import socket
import threading
from typing import Tuple
import argparse

from PyMultiplex.Threads.MultiplexServerThread import MultiplexServerThread
from PyMultiplex.utils.Logger import Logger
from PyMultiplex.utils.consts import MAX_CLIENTS


class MultiplexServer:
    def __init__(self, listen_address: Tuple[str, int]):
        self._multiplex_socket = socket.socket()
        self._multiplex_socket.bind(listen_address)
        self._max_clients = MAX_CLIENTS
        self._logger = Logger(self)
        self.ident = id(self)

    def start(self):
        self._multiplex_socket.listen(self._max_clients)
        self._logger.info(f"Listening on {self._multiplex_socket.getsockname()}")

        while True:
            # for every new tool connected, create new set of channels
            client_socket, client_address = self._multiplex_socket.accept()
            self._logger.info(f"Connected by {client_address}")
            multiplex_thread = MultiplexServerThread(client_socket)
            threading.Thread(target=multiplex_thread.start).start()


def main():
    parser = argparse.ArgumentParser(description='Run MultiplexServer')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to')
    parser.add_argument('--port', type=int, default=8080, help='Port to bind to')
    args = parser.parse_args()
    server = MultiplexServer((args.host, args.port))
    server.start()

if __name__ == '__main__':
    main()
