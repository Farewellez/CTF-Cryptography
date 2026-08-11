import hashlib
import requests
from Crypto.Cipher import AES

URL = "https://aes.cryptohack.org/passwords_as_keys"

def encrypt():
    return bytes.fromhex(requests.get(f"{URL}/encrypt_flag/").json()['ciphertext'])

def decrypt(ciphertext: bytes, password_hash: bytes):
    cipher = AES.new(password_hash, AES.MODE_ECB)
    try:
        decrypted = cipher.decrypt(ciphertext)
    except ValueError as e:
        return {"error": str(e)}

    return decrypted

with open("/mnt/d/my-kisah/crypto/2.cryptohack/3.Symmetric-Cryptography/write-up/chall9/words") as f:
    words = [w.strip() for w in f.readlines()]

ct = encrypt()
print(f"trying key, take some coffe break first while waiting...")
for i in range(len(words)):
    key = hashlib.md5(words[i].encode()).digest()
    pt = decrypt(ct, key)
    if b"crypto" in pt:
        print(pt.decode())
        break
