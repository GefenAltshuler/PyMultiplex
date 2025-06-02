from Multiplex.MultiplexClient import MultiplexClient

def main():
    server = MultiplexClient(('127.0.0.1', 8080), ('127.0.0.1', 1726))
    # server = MultiplexClient(('127.0.0.1', 8080), ('altshuler.xyz', 22))
    server.start()

if __name__ == '__main__':
    main()