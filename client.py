# CLI

import socket
import json
import sys
from models import Route
from config import PASSWORD, HOST, KDC_PORT, CLIENT_USERNAME
from crypto import encrypt, decrypt

# Global Information of CLI node
id = None
key = None

# Input username password
username = CLIENT_USERNAME
password = PASSWORD

if (len(sys.argv) > 1):
    KDC_PORT = int(sys.argv[1])

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    print("Connecting with KDC on PORT:", KDC_PORT, "...")
    try:
        sock.connect((HOST, KDC_PORT))
    except:
        print("ERR: Unable to connect with KDC.")
        exit()

    data = Route("login", {'username': username, 'password': password})
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
