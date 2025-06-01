import threading
import logging
import socket

from multiplex import read_channels_socket, read_channels_queues, read_messages

TARGET_ADDRESS = ('209.38.142.101', 22)

def main():
    communication_socket = socket.socket()
    communication_socket.connect(TARGET_ADDRESS)
    logging.info(f'connecting to {TARGET_ADDRESS}')

    t1 = threading.Thread(target=read_channels_socket, args=(communication_socket,))
    t2 = threading.Thread(target=read_channels_queues)

    t1.start()
    t2.start()

    read_messages(communication_socket)

    t1.join()
    t2.join()


if __name__ == '__main__':
    main()
