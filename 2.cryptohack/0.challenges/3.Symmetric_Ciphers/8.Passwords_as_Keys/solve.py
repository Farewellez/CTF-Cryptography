import requests
import hashlib
from Crypto.Cipher import AES
from tqdm import tqdm

url = "https://aes.cryptohack.org/passwords_as_keys"

def encrypt_flag():
    try:
        data = requests.get(f"{url}/encrypt_flag/")
        ciphertext = data.json()['ciphertext']
    except ConnectionError:
        return "error"
    return ciphertext

def decrypt(ciphertext):
    ct =  bytes.fromhex(ciphertext)
    with open("words") as f:
        words = [w.strip() for w in f.readlines()]

    keys = [hashlib.md5(k.encode()).digest() for k in words]
    for i in tqdm(range(len(keys)), total=len(keys), desc="matching hash "):
        cipher = AES.new(keys[i], AES.MODE_ECB)
        if b'crypto' in cipher.decrypt(ct):
            flag = cipher.decrypt(ct)
            return flag
    return ""

ct = encrypt_flag()
# print(ct)
flag = decrypt(ct)
if flag:
    print(f"flag: {flag.decode()}")