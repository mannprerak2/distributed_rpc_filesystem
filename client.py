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

# Files last fetched
files = {}

if (len(sys.argv) > 1):
    KDC_PORT = int(sys.argv[1])


def request(port, path, body):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((HOST, port))
    except:
        print("ERR: Unable to connect to", port)
        exit()

    data = Route(path, body)
    data = encrypt(data.serialize())
    status = sock.sendall(data)

    if status == None:
        response = sock.recv(1024)
        response = decrypt(response)
        response = json.loads(response)

        return response
    else:
        print("Could not send the request")
        exit()


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

    sock.close()

    if (received == b'\0'):
        print("Wrong credentials")
        exit()
    else:
        received = decrypt(received)
        received = json.loads(received)

        id = received['id']
        key = bytes.fromhex(received['key'])
        print("Log in successful. Assigned id:", id, "\n")

        while(True):
            prompt = ">> "
            command = input(prompt)

            if command == "exit":
                exit()
            elif command == "ls":
                response = request(KDC_PORT, "ls", None)
                files = response['files']

                for each in files:
                    print(each['name'], end=' ')
                print()
