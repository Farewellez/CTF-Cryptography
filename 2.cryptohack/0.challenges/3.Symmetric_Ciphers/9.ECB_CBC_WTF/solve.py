import requests
from tqdm import tqdm

url = "https://aes.cryptohack.org/ecbcbcwtf"

def fixed_xor(b1,b2):
    return bytes([x ^ y for x, y in zip(b1,b2)])

def encrypt():
    data = requests.get(f"{url}/encrypt_flag/")
    ciphertext = data.json()['ciphertext']
    return ciphertext

def decrypt(ciphertext):
    iv = bytes.fromhex(ciphertext)[:16]
    ct = bytes.fromhex(ciphertext)[16:]

    blocks = [ct[i:i+16] for i in range(0,len(ct),16)]
    pt = b""
    for i in tqdm(range(len(blocks)), total=len(blocks), desc="decrypting ciphertext "):
        # print(blocks[i].hex())
        data = requests.get(f"{url}/decrypt/{blocks[i].hex()}/")
        decrypted = data.json()['plaintext']
        # print(decrypted)
        if i == 0:
            pt += fixed_xor(iv, bytes.fromhex(decrypted))
        else:
            pt += fixed_xor(blocks[i - 1], bytes.fromhex(decrypted))
    return pt

ct = encrypt()
pt = decrypt(ct)
if pt:
    print(f"Flag: {pt.decode()}")