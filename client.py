import socket
import logging
import threading
from multiplex import read_messages, build_message, Message, get_greeting_channel

SERVER_ADDRESS = ('127.0.0.1', 8080)

# todo: support only 1 ForYou client
def read_thread(client_socket, main_sock, channel):
    data = client_socket.recv(1024)
    message = build_message(channel, Message.data, data)
    main_sock.sendall(message)

def write_thread(client_socket, main_sock, channel):
    while True:
        data = read_messages(main_sock)
        if not data: continue
        client_socket.sendall(data)


def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('0.0.0.0', 7d190))
    server_socket.listen(10)
    logging.info(f"[ForYou] Listening on {SERVER_ADDRESS}")

    while True:
        # accept new client
        client_socket, client_address = server_socket.accept()
        logging.info(f"[ForYou] Connected by {client_address}")

        sock = socket.socket()
        sock.connect(SERVER_ADDRESS)
        logging.info(f'[ForYou] Connected to {SERVER_ADDRESS}')

        channel = get_greeting_channel(sock)
        t1 = threading.Thread(target=read_thread, args=(client_socket, sock, channel))
        t2 = threading.Thread(target=write_thread, args=(client_socket, sock, channel))

        t1.start()
        t2.start()

if __name__ == '__main__':
    main()