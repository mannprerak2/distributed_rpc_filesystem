# Key Distribution Center
import os
import sys
import json
import socketserver

from models import FileSystem, Route
from crypto import encrypt, decrypt

# Stores id -> filesystem_node
filesystems = {}

class MyTCPHandler(socketserver.BaseRequestHandler):
    def handle(self):
        self.data = self.request.recv(1024).strip()
        route = decrypt(self.data)
        route = Route.fromrequest(route)

        if (route.get_sel() == "init"):
            # A file system node is initialising the connection
            fs = FileSystem(len(filesystems) + 1)

            # Save the generated id and key pair (for faster lookups)
            filesystems[fs.get_id()] = fs
            response = fs.serialize()

            print("Registering file system node with id:", fs.get_id())
            response = encrypt(response)
            
            self.request.sendall(response)

if __name__ == "__main__":
    HOST, PORT = "localhost", int(sys.argv[1])

    with socketserver.TCPServer((HOST, PORT), MyTCPHandler) as server:
        server.serve_forever()