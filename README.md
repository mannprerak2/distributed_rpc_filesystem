# dis_project

A distributed RPC file system utilising symmetric key cryptography. Made with Python3.

### Notes -

- Generate 16 byte key for every client node and file system node.

- KDC also generates a 16 byte key for the session key.

- Use AES encryption.

- Filesystem nodes would also be TCP servers

### Setup -

1. Create Python3 virtual environment

```bash
    python3 -m venv venv/
```

2. Launch virtual environment

```bash
    source venv/bin/activate
```

3. Install dependencies

```bash
    pip install -r requirements.txt
```

...
