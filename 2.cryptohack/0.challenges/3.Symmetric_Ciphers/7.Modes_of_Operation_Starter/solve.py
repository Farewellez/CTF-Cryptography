import requests

url = "https://aes.cryptohack.org/block_cipher_starter"

def encrypt_flag():
    data = requests.get(f"{url}/encrypt_flag/")
    ciphertext = data.json()["ciphertext"]
    return ciphertext

def decrypt(ct):
    data = requests.get(f"{url}/decrypt/{ct}/")
    # return data.json()
    plaintext = data.json()["plaintext"]
    return plaintext

ct = encrypt_flag()
# print(ct)
pt = decrypt(ct)
flag = bytes.fromhex(pt)
print(flag)