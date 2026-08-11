import requests

URL = "https://aes.cryptohack.org/symmetry"

def encrypt():
    return requests.get(f"{URL}/encrypt_flag/").json()['ciphertext']

def decrypt(ciphertext: str, iv: str):
    return requests.get(f"{URL}/encrypt/{ciphertext}/{iv}/").json()['ciphertext']

ct = encrypt()
iv = ct[:16*2]
flag = bytes.fromhex(decrypt(ct[16*2:], iv))
print(flag.decode())