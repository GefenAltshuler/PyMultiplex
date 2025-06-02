import socket
from queue import Queue
from PyMultiplex.Channel.Message import Message, MessageCode
from PyMultiplex.utils.Logger import Logger


class ChannelSocket:
    def __init__(self, channel: int, remote_socket: socket.socket):
        super().__init__()
        self._queue = Queue()
        self._remote_sock: socket.socket = remote_socket
        self._channel = channel
        self.is_open = True

    def get(self):
        return self._queue.get()

    def put(self, data: bytes):
        return self._queue.put(data)

    def recv(self, _):
        return self.get()

    def sendall(self, data: bytes):
        data_message = Message(self._channel, MessageCode.data, data)
        self._remote_sock.sendall(data_message.to_bytes())

    def close(self):
        if self.is_open:
            self.is_open = False
            self.remote_close_channel()
        else:
            Logger.inner_debug(f'socket of channel {self._channel} already closed, passing', ChannelSocket)

    def remote_close_channel(self):
        Logger.inner_debug(f'Closing channel {self._channel}', ChannelSocket)
        close_channel_message = Message(self._channel, MessageCode.close)
        self._remote_sock.sendall(close_channel_message.to_bytes())


