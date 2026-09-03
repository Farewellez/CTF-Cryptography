import requests
import json

BASE_URL = "https://aes.cryptohack.org/lazy_cbc"
BS = 16

def encrypt(ciphertext: bytes) -> str:
    r = requests.get(f"{BASE_URL}/receive/{ciphertext.hex()}/")
    data = r.json()
    if 'error' in data:
        errr = data['error']
        return errr
    pt = data['ciphertext']
    return pt

def get_flag(key: bytes):
    r = requests.get(f"{BASE_URL}/get_flag/{key.hex()}/")
    data = r.json()
    return data['plaintext']

c1 = b"\x00"*16
c2 = b"\x00"*16
c3 = c1

payload = c1 + c2 + c3
ct = encrypt(payload).split(": ")[1]
print(f"ciphertext: {ct}")

pt_block1 = bytes.fromhex(ct)[:16]
pt_block3 = bytes.fromhex(ct)[16*2:]

key = b"".join((bytes([x ^ y]) for x,y in zip(pt_block1, pt_block3)))
print(key)

flag = bytes.fromhex(get_flag(key))
print(flag)