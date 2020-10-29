HOST = "localhost"
KDC_PORT = 3000

KEY = bytes.fromhex("6184e0c8351851b7ca8d176fce40e793")
PASSWORD = "password"
CLIENT_USERNAME = "admin"

# Available commands, key->name : value -> usage
COMMANDS = {
    "ls": "ls - list files in current directory",
    "cat": "cat <file-name> - print contents of a file",
    "pwd": "pwd - print working directory",
    "cp": "cp <source-file> <target-file-name> -  copy a file"
}
