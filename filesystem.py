# File System Node

import socket
import json
import sys
from crypto import encrypt, decrypt
from models import Route

HOST, PORT = "localhost", int(sys.argv[1])

# Global Information of FS node
id = None
key = None

# Initialisation - get unique ID and key from KDC

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    sock.connect((HOST, PORT))

    data = Route("init", None)
    data = encrypt(data.serialize())

    # Connect to server and send data
    sock.sendall(data)

    # Receive data from the server and shut down
    received = sock.recv(1024)
    received = decrypt(received)
    received = json.loads(received)

    id = received['id']
    key = bytes.fromhex(received['key'])
    print("Node successfully registered with id:", id)
