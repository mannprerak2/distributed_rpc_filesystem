# CLI

import socket
import json
import sys
from models import Route
from keys import PASSWORD
from crypto import encrypt, decrypt

HOST, PORT = "localhost", int(sys.argv[1])

# Global Information of CLI node
id = None
key = None

# Input username password
username = "admin"
password = PASSWORD

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    sock.connect((HOST, PORT))

    data = Route("login", { 'username': username, 'password': password })
    data = encrypt(data.serialize())

    # Connect to server and send data
    sock.sendall(data)

    # Receive data from the server and shut down
    received = sock.recv(1024)

    if (received == b'\0'):
        print("Wrong credentials")
        exit()
    else:
        received = decrypt(received)
        received = json.loads(received)

        id = received['id']
        key = bytes.fromhex(received['key'])
        print("Successfully received key with id:", id)

