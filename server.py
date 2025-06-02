import socket
import logging
import threading
from utils import get_channel_number
from multiplex import read_messages, build_message, Message, channels, send_greeting_channel, channels

SERVER_ADDRESS = ('0.0.0.0', 8080)
MAX_CLIENTS = 10

def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(SERVER_ADDRESS)
    server_socket.listen(MAX_CLIENTS)
    logging.info(f"Listening on {SERVER_ADDRESS}")

    while True:
        # accept new client
        client_socket, client_address = server_socket.accept()
        logging.info(f"Connected by {client_address}")

        # open new channel
        channel = get_channel_number(channels)
        queue = socket.socketpair()
        channels[channel] = (queue, client_socket)

        send_greeting_channel(client_socket, channel)

        message = build_message(channel, Message.open)
        client_socket.send(message)

        t = threading.Thread(target=read_messages, args=(client_socket,))
        t.start()



if __name__ == '__main__':
    main()