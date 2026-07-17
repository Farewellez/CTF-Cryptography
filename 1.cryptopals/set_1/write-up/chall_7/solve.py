# AES in ECB mode
import base64
from Crypto.Cipher import AES

with open("/mnt/d/my-kisah/crypto/1.cryptopals/files/7.txt") as f:
    buffer = "".join(line.strip() for line in f)

ct = base64.b64decode(buffer)
key = "YELLOW SUBMARINE"

cipher = AES.new(key.encode(), AES.MODE_ECB)
pt = cipher.decrypt(ct)
print(pt.decode())
