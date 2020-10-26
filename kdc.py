# Key Distribution Center
import os
import sys
import socketserver
import json

class FileSystem:
    def __init__(self, id):
        self.id = str(id)
        self.key = os.urandom(16)

    def get_key(self):
        return self.key

    def get_id(self):
        return self.id

    def serialize(self):
        return json.dumps({ 'id': self.id, 'key': self.key.hex() })

# Stores id -> filesystem_node
filesystems = {}

class MyTCPHandler(socketserver.BaseRequestHandler):
    def handle(self):
        self.data = self.request.recv(1024).strip()
        route = str(self.data, 'utf-8')

        if (route == "init"):
            # A file system node is initialising the connection
            fs = FileSystem(len(filesystems) + 1)

            # Save the generated id and key pair (for faster lookups)
            filesystems[fs.get_id()] = fs
            response = fs.serialize()

            print("Registering file system node with id:", fs.get_id())
            response = bytes(response, 'utf-8')
            
            self.request.sendall(response)

if __name__ == "__main__":
    HOST, PORT = "localhost", int(sys.argv[1])

    with socketserver.TCPServer((HOST, PORT), MyTCPHandler) as server:
        server.serve_forever()