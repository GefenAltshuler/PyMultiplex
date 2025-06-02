import socket

class ChannelSocket:
    def __init__(self, network_socket):
        self.rx, self.rw = socket.socketpair()
        self._network_socket: socket.socket = network_socket

    def recv(self, buffer_size):
        return self.rx.recv(buffer_size)

    def sendall(self, data: bytes):
        return self.rw.sendall(data)