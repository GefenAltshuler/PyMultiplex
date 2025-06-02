import socket
from queue import Queue
from Channel.Message import Message, MessageCode


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
        self.is_open = False

    def get_closing_message(self):
        close_channel_message = Message(self._channel, MessageCode.close)
        return self.put(close_channel_message.to_bytes())  # todo: understand how this message will come to the remote endpoint ## todo: lmao hahahah lol


