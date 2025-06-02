from PyMultiplex import MultiplexClient

def main():
    server = MultiplexClient(('127.0.0.1', 8080), ('wtfismyip.com', 80), 1726)
    server.start()

if __name__ == '__main__':
    main()