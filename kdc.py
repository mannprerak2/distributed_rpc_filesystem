# Key Distribution Center
import os
import sys
import json
import socketserver

from models import FileSystem, Client, Route
from crypto import encrypt, decrypt
from config import HOST, KDC_PORT

# Stores id -> filesystem_node
filesystems = {}

# Stores id -> client_node
clients = {}

if (len(sys.argv) > 1):
    KDC_PORT = int(sys.argv[1])


class MyTCPHandler(socketserver.BaseRequestHandler):
    def handle(self):
        self.data = self.request.recv(1024).strip()
        route = decrypt(self.data)
        route = Route.fromrequest(route)

        if (route.get_sel() == "init"):
            # A file system node is initialising the connection
            fs = FileSystem(len(filesystems) + 1,
                            port=route.body['port'], files=route.body['files'])

            # Save the generated id and key pair (for faster lookups)
            filesystems[fs.get_id()] = fs
            response = fs.serialize()

            print("Registering file system node with id:", fs.get_id())
            response = encrypt(response)

            self.request.sendall(response)

        elif (route.get_sel() == "login"):
            if (route.body['username'] == "admin" and route.body['password'] == "password"):
                # Successful login
                cl = Client(len(clients) + 1)
                clients[cl.get_id()] = cl
                response = cl.serialize()

                print("Successful login and key generated for client:", cl.get_id())
                response = encrypt(response)

                self.request.sendall(response)
            else:
                # Login failed
                self.request.sendall(bytes('\0', 'utf-8'))


if __name__ == "__main__":
    with socketserver.TCPServer((HOST, KDC_PORT), MyTCPHandler) as server:
        print("Running KDC server on PORT:", KDC_PORT, "...")
        server.serve_forever()
