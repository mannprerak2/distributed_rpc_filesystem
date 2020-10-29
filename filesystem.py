# File System Node

import os
import socket
import json
import sys
import argparse
from crypto import encrypt, decrypt
from models import Route
from config import HOST, KDC_PORT

parser = argparse.ArgumentParser()
parser.add_argument(
    '--port', help="Port number for filesystem socketserver", required=True)
parser.add_argument(
    '--path', help="Path of the directory to be mounted", required=True)
parser.add_argument('--kdc', help="Port number for KDC")

args = parser.parse_args()

# Global Information of FS node
id = None
key = None

# PATH - path of directory to be mounted
PATH = args.path

# PORT - port number for filesystem server
PORT = int(args.port)

if (args.kdc != None):
    KDC_PORT = int(args.kdc)

# Initialisation - get unique ID and key from KDC

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    print("Connecting with KDC on PORT:", KDC_PORT, "...")
    try:
        sock.connect((HOST, KDC_PORT))
    except:
        print("ERR: Unable to connect with KDC.")
        exit()

    try:
        files = os.listdir(PATH)
    except:
        print("Not a valid path provided")
        exit()

    print("Registering FS node with KDC ...")
    data = Route("init", {'port': PORT, 'files': files})
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
