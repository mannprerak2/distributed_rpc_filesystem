import base64
import hashlib
import json
from Cryptodome.Cipher import AES
from Cryptodome.Random import get_random_bytes

# Shared symmetric key
from keys import KEY

def encrypt(raw):
    BS = AES.block_size
    pad = lambda s: s + (BS - len(s) % BS) * chr(BS - len(s) % BS)

    raw = base64.b64encode(pad(raw).encode('utf8'))
    iv = get_random_bytes(AES.block_size)

    cipher = AES.new(key=KEY, mode= AES.MODE_CFB, iv= iv)
    return base64.b64encode(iv + cipher.encrypt(raw))

def decrypt(enc):        
    unpad = lambda s: s[:-ord(s[-1:])]

    enc = base64.b64decode(enc)
    iv = enc[:AES.block_size]
    cipher = AES.new(KEY, AES.MODE_CFB, iv)
    return unpad(base64.b64decode(cipher.decrypt(enc[AES.block_size:])).decode('utf8'))

# For testing purpose
if __name__ == "__main__":
    payload = json.dumps({ 'id': "123", 'key': "123438473" })
    print(payload)

    data = encrypt(payload)
    print(data)

    decrypted = decrypt(data)
    print(decrypted)