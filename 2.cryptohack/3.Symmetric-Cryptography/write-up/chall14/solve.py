import requests

URL = "https://aes.cryptohack.org/bean_counter"

def encrypt():
    return requests.get(f"{URL}/encrypt/").json()['encrypted']

def fixed_xor(b1,b2):
    return bytes([x ^ y for x,y in zip(b1,b2)])

data = bytes.fromhex(encrypt())
with open("flag.png", "wb") as f:
    f.write(data)

# https://medium.com/@0xwan/png-structure-for-beginner-8363ce2a9f73
# iv XOR known_pt = ct
# known_pt XOR ct = iv
known_pt = open("/mnt/d/my-kisah/crypto/2.cryptohack/3.Symmetric-Cryptography/write-up/chall14/header.png", "rb").read()
flag = b""
iv = fixed_xor(known_pt, data[:16])
for i in range(0,len(data),16):
    flag += fixed_xor(data[i:i+16], iv)

with open("recover.png", "wb") as f:
    f.write(flag)
    