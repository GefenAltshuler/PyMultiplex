from PyMultiplex.Multiplex.MultiplexServer import MultiplexServer

def main():
    server = MultiplexServer(('0.0.0.0', 8080))
    server.start()

if __name__ == '__main__':
    main()