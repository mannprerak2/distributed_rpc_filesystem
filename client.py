# CLI

import os
import sys
import json
import socket
from models import Route
from config import PASSWORD, HOST, KDC_PORT, CLIENT_USERNAME, COMMANDS
from crypto import encrypt, decrypt

# Global Information of CLI node
id = None
key = None

# Input username password
username = CLIENT_USERNAME
password = PASSWORD

# Files last fetched
files = {}

# Session keys (port number -> session key mapping)
session_keys = {}

if (len(sys.argv) > 1):
    KDC_PORT = int(sys.argv[1])


def get_fs_port(filename):
    # Get port number of FS node which contains filename
    for each in files:
        if each['name'] == filename:
            return int(each['port']), each['id']
    return None, None


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


def get_session_key(port, id):
    # print("Getting session key for FS", id)
    # 1. Send request to KDC with FS id
    # 2. Get session key and its encrypted version (using FS's key)
    # 3. Save to global mapping

    response = request(KDC_PORT, "comm", {'id': id})

    session_key = response['key']
    encrypted_session_key = response['encrypted']

    session_keys[port] = {
        'key': bytes.fromhex(session_key),
        'encrypted': bytes.fromhex(encrypted_session_key)
    }


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
            command = input(prompt).strip()

            words = command.split(' ')
            if len(words) < 1:
                continue

            if words[0] == "exit":
                exit()

            elif words[0] == "help":
                if len(words) != 2:
                    print("Available Commands - ")
                    for key in COMMANDS.keys():
                        print(COMMANDS[key])
                elif words[1] not in COMMANDS:
                    print(words[1], "- No such command.")
                else:
                    print("Usage:", COMMANDS[words[1]])

            elif words[0] == "ls":
                response = request(KDC_PORT, "ls", None)
                files = response['files']

                for each in files:
                    print(each['name'], end=' ')
                print()

            elif words[0] == "pwd":
                print("/")

            elif words[0] == "clear":
                os.system('clear')

            elif words[0] not in COMMANDS:
                print(command, "- No such command.")

            # Other commands that use files
            else:
                filename = words[1]
                port, id = get_fs_port(filename)

                if (port == None):
                    print("No such file")
                else:
                    # After this, session_keys contains the key and encrypted key for required FS
                    if port not in session_keys:
                        get_session_key(port, id)

                    # The session key and encrypted session key for FS at port
                    session_key = session_keys[port]['key']
                    encrypted_session_key = session_keys[port]['encrypted']

                    # Prove to filesystem that session key is correct
                    response = request(
                        port, "init", {'key': encrypted_session_key.hex()}
                    )

                    nonce = int(response['nonce'])

                    # Send incremented nonce and the RPC
                    response = request(
                        port, "confirm",
                        {'nonce': nonce + 1, 'command': command}
                    )

                    print(response['result'])
