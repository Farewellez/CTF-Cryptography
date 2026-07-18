# Implement CBC mode
import base64
from Crypto.Cipher import AES

def fixed_xor(b1: bytes, b2: bytes):
    return bytes([x ^ y for x, y in zip(b1,b2)])

def decrypt_aes_cbc(ciphertext: bytes, key: bytes, iv: bytes):
    blocks = [ciphertext[i:i+16] for i in range(0,len(ciphertext),16)]
    cipher = AES.new(key, AES.MODE_ECB)
    pt = b""

    for i in range(len(blocks)):
        cti = cipher.decrypt(blocks[i])
        if i == 0:
            pt += fixed_xor(cti, iv)
            continue
        pt += fixed_xor(blocks[i-1], cti)
    
    return pt

with open("/mnt/d/my-kisah/crypto/1.cryptopals/files/10.txt") as f:
    buffer = "".join(line.strip() for line in f)

ct = base64.b64decode(buffer)
key = b"YELLOW SUBMARINE"
iv = bytes([0]) * 16
pt = decrypt_aes_cbc(ct, key, iv)
print(pt.decode(errors="ignore"))
