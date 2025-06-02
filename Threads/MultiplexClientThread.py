import socket
from typing import Tuple

from Threads.MultiplexThread import MultiplexThread


class MultiplexClientThread(MultiplexThread):
    def __init__(self, target_server: Tuple[str, int], *args, **kwargs) -> None:
        self._target_server = target_server
        super().__init__(*args, **kwargs)

    def _get_pipe_socket(self) -> socket.socket:
        sock = socket.socket()
        sock.connect(self._target_server)

        return sock
