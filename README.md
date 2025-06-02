# PyMultiplex

## Overview

**PyMultiplex** is a Python package that allows you to open several **virtual channels over a single socket connection**, similar to how SSH handles multiple logical sessions over one connection.

Originally built to support reverse tunneling, PyMultiplex is versatile and suitable for any environment where only **one socket connection is allowed** between endpoints. Simply run the **Multiplex server** on one end and the **Multiplex client** on the other, and you can open many "virtual sockets." This is **completely transparent to your application**.

The server listens for incoming ports requested by the client. For each new connection on those forwarded ports, it creates a **new virtual channel** over the shared socket.

You can learn more about reverse tunneling here:
- [Wikipedia - Reverse Connection](https://en.wikipedia.org/wiki/Reverse_connection)  
- [Qbee.io - Reverse SSH Tunneling Guide](https://qbee.io/misc/reverse-ssh-tunneling-the-ultimate-guide/)

## How It Works

PyMultiplex consists of two main components:

1. **`MultiplexServer`**  
   Listens for incoming client connections and spawns a thread per client. It also listens for port-forwarding requests from the client, and for each new connection on a forwarded port, it creates a virtual pipe (a new thread) over the existing connection.

2. **`MultiplexClient`**  
   Connects to the `MultiplexServer`, requests remote port forwarding, and forwards data received on that port to a specified target server (functionally identical to `ssh -R`).

## Installation

To install the package:

```bash
pip install PyMultiplex
```

Or install directly from GitHub:

```bash
pip install git+https://github.com/GefenAltshuler/PyMultiplex@main
```

Make sure the `pip` binary is in your system `PATH` — this will give you access to the `multiplex` command.

## Usage

### Command Line

PyMultiplex supports two modes: `server` and `client`. Here's how to use them in **reverse tunnel** mode:

#### Server

```bash
multiplex server --bind 0.0.0.0 --port 8080
```

#### Client

```bash
multiplex client \
  --host 127.0.0.1 \
  --port 8080 \
  --to-host wtfismyip.com \
  --to-port 80 \
  --remote-forward-port 1726
```

Now you can connect to the server's port `1726`, and the traffic will be tunneled to `wtfismyip.com:80` via the client:

```bash
curl http://127.0.0.1:1726/json -H "Host: wtfismyip.com"
```

Example output:
```json
{
  "YourFuckingLocation": "Santa Clara, CA, United States",
  "YourFuckingCity": "Santa Clara",
  "YourFuckingCountry": "United States",
  "YourFuckingCountryCode": "US"
}
```

### Python Code

You can also use PyMultiplex programmatically in Python. (Additional examples are in the `Examples/` folder.)

#### Server

```python
from PyMultiplex import MultiplexServer

def main():
    server = MultiplexServer(('0.0.0.0', 8080))
    server.start()

if __name__ == '__main__':
    main()
```

#### Client

```python
from PyMultiplex import MultiplexClient

def main():
    client = MultiplexClient(('127.0.0.1', 8080), ('wtfismyip.com', 80), 1726)
    client.start()

if __name__ == '__main__':
    main()
```

This sets up a **remote port 1726** on the server. Each connection to this port results in a new **virtual channel** being created between the server and client. Data is piped bidirectionally between the real and virtual sockets, ensuring full transport transparency.

### Architecture Diagram
As in the example above, let's assume the client requested to remote-forward all traffic from port 1726 to google.com on port 443

![Program Flow](Images/diagram.png)
