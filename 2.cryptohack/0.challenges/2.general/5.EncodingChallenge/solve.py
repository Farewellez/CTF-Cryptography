import json
import base64
import codecs
from Crypto.Util.number import long_to_bytes
from tqdm import tqdm
from pwn import *

host = "socket.cryptohack.org"
port = 13377
context.log_level = 'error'

io = remote(host, port)
for i in tqdm(range(101), desc="Just a second...", unit="flag"):
    raw_data = json.loads(io.recvline())
    if "flag" in raw_data:
        print("\nGotcha! here's the flag:")
        print(raw_data["flag"])
        break
    encoding = raw_data["type"]
    encoded = raw_data["encoded"]

    if encoding == "base64":
        decoded = base64.b64decode(encoded).decode()
    elif encoding == "hex":
        decoded = bytes.fromhex(encoded).decode()
    elif encoding == "rot13":
        decoded = codecs.decode(encoded, 'rot_13')
    elif encoding == "bigint":
        decoded = long_to_bytes(int(encoded,16)).decode()
    elif encoding == "utf-8":
        decoded = bytes(encoded).decode()
    payload = {"decoded":decoded}
    io.sendline(json.dumps(payload).encode())

io.close()