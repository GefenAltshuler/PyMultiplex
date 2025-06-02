from PyMultiplex.Multiplex.MultiplexServer import MultiplexServer
from PyMultiplex.Multiplex.MultiplexClient import MultiplexClient
import argparse


def main():
    parser = argparse.ArgumentParser(
        description="A tool for transferring data across multiple virtual channels over a single socket connection, "
                    "powered by a multiplexing architecture. By default, the tool operates in reverse-tunnel mode "
                    "(similar to ssh -R), allowing inbound connections from the server to be forwarded through the "
                    "client."
    )

    subparsers = parser.add_subparsers(dest="mode", required=True, help="Mode to run")

    # Client subparser
    client_parser = subparsers.add_parser("client", help="Run as multiplex client")
    client_parser.add_argument("--host", required=True, help="Multiplex Server to connect to")
    client_parser.add_argument("--port", required=True, type=int, help="Multiplex Server port to connect to")

    client_parser.add_argument("--to-host", required=True, help="Target server address to connect to")
    client_parser.add_argument("--to-port", required=True, type=int, help="Target server port to connect to")

    client_parser.add_argument("--remote-forward-port", required=True, type=int, help="Remote forward "
                                                                                      "port the Multiplex server should "
                                                                                      "open for data transfer")

    # Server subparser
    server_parser = subparsers.add_parser("server", help="Run as multiplex server")
    server_parser.add_argument("--bind", default="0.0.0.0", help="Address to bind multiplex server")
    server_parser.add_argument("--port", type=int, default=1234, help="Port to bind the multiplex server")

    args = parser.parse_args()

    if args.mode == "client":
        server_address = (args.host, args.port)
        target_address = (args.to_host, args.to_port)
        remote_forward_port = args.remote_forward_port

        server = MultiplexClient(server_address, target_address, remote_forward_port)
        server.start()

    elif args.mode == "server":
        listen_address = (args.bind, args.port)

        server = MultiplexServer(listen_address)
        server.start()


if __name__ == "__main__":
    main()