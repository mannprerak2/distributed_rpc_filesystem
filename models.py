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

# To-Do: Handle all edge cases when body is None
class Route:
    def __init__(self, sel, body):
        self.sel = sel
        self.body = body

    @classmethod
    def fromrequest(cls, serialized):
        data = json.loads(serialized)
        
        if ('body' not in data):
            return cls(data['sel'], None)
        return cls(data['sel'], data['body'])

    def serialize(self):
        if (self.body == None):
            return json.dumps({ 'sel': self.sel })
        return json.dumps({ 'sel': self.sel,  body: self.body})

    def get_sel(self):
        return self.sel