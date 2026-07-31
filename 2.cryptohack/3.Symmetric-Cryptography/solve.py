import requests

BASE_URL = "https://aes.cryptohack.org/ecbcbcwtf/"
BS = 16

def fixed_xor(b1: bytes, b2: bytes):
    return bytes([x ^ y for x,y in zip(b1,b2)])

def decrypt(ciphertext: bytes):
    ct = ciphertext.hex()
    r = requests.get(f"{BASE_URL}/decrypt/{ct}")
    data = r.json()
    cti = data['plaintext']
    return bytes.fromhex(cti)

def encrypt():
    r = requests.get(f"{BASE_URL}/encrypt_flag/")
    data = r.json()
    ct = data['ciphertext']
    return ct

def split_blocks(ciphertext: bytes):
    return [ciphertext[i:i+BS] for i in range(0, len(ciphertext), BS)]

ciphertext = bytes.fromhex(encrypt())
iv = ciphertext[:16]
ct = ciphertext[16:]
pt = []

block_ct = split_blocks(ct)
for i in range(len(block_ct)):
    cti = decrypt(block_ct[i])
    if i == 0:
        xord = fixed_xor(cti, iv)
        pt.append(xord)
        continue
    xord = fixed_xor(cti, block_ct[i-1])
    pt.append(xord)

print(b"".join(pt).decode())