import requests
URL = "https://aes.cryptohack.org/block_cipher_starter"

def encrypt():
    return bytes.fromhex(requests.get(f"{URL}/encrypt_flag/").json()['ciphertext'])

def decrypt(ciphertext: bytes) -> bytes:
    return bytes.fromhex(requests.get(f"{URL}/decrypt/{ciphertext.hex()}/").json()['plaintext'])

ct = encrypt()
flag = decrypt(ct).decode()
print(flag)