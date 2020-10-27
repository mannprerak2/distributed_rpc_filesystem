import os
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

class Route:
    def __init__(self, sel, body):
        self.sel = sel
        self.body = body

    def __init__(self, serialized):
        data = json.loads(serialized)
        self.sel = data.sel
        self.body = data.body

    def serialize(self):
        return json.dumps({ 'sel': self.sel,  body: self.body})