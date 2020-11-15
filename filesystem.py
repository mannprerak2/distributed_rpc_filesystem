# File System Node

import os
import sys
import json
import socket
import random
import argparse
import socketserver
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


def request(port, path, body):
    # To-Do: Use single common definition of this function

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

last_nonce = 0

# ====================RPC===============================

def cat(filename):
    file_path = os.path.join(PATH, filename)
    text = open(file_path, 'r').read()
    return json.dumps({'result': text})


def cp(oldFile, newFile):
    og_file = os.path.join(PATH, oldFile)
    new_file = os.path.join(PATH, newFile)
    response={}
    if (os.path.exists(os.path.join(PATH, new_file)) == False):
        try:
            text = open(og_file, mode='r').read()
            copy = open(new_file, mode='w+')
            copy.write(text)
            response = json.dumps(
                {'result': 'Created copy successfuly'})

            # Update KDC about the new file
            request(KDC_PORT, "update", {
                    'id': id, 'files': os.listdir(PATH)
                    })

        except:
            response = json.dumps(
                {'result': 'Copy creation failed'})
    else:
        response = json.dumps(
            {'result': 'File already exists'})
    return response
# =======================================================



class MyTCPHandler(socketserver.BaseRequestHandler):
    def handle(self):
        global last_nonce

        self.data = self.request.recv(1024).strip()
        route = decrypt(self.data)
        route = Route.fromrequest(route)

        if (route.get_sel() == "init"):
            print("A client node is trying to authenticate itself")
            # Client has sent the session key encrypted using this FS's key
            enc_key = route.body['key']

            try:
                session_key = decrypt(bytes.fromhex(enc_key), key)
                last_nonce = random.randrange(1000)

                response = json.dumps({'nonce': str(last_nonce)})
            except:
                response = json.dumps({'error': "1"})
            finally:
                response = encrypt(response)
                self.request.sendall(response)

        elif (route.get_sel() == "confirm"):
            print("Received nonce and RPC")
            nonce = int(route.body['nonce'])

            if (nonce == last_nonce + 1):
                print("Execute:", route.body['command'])

                command = route.body['command']
                words = command.split(' ')

                if (words[0] == "cat"):
                    response = cat(words[1])

                elif (words[0] == "cp"):
                    response = cp(words[1], words[2])
            else:
                response = json.dumps({'result': 'Authentication failed'})

            response = encrypt(response)
            self.request.sendall(response)


with socketserver.TCPServer(("localhost", PORT), MyTCPHandler) as server:
    print("Running file server on PORT:", PORT, "...")
    server.serve_forever()
