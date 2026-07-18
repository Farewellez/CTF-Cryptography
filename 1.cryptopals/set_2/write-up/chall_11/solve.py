# An ECB/CBC detection oracle
import os
import random
from Crypto.Cipher import AES

def keygen_aes(keysize: int):
    return os.urandom(keysize)

def salted(plaintext: bytes):
    count = random.randrange(5,11)
    prefix = os.urandom(count)
    suffix = os.urandom(count)
    return prefix + plaintext + suffix

def pkcs7(plaintext: bytes, block_size = 16): return plaintext + (bytes([(block_size - (len(plaintext) % block_size))]) * (block_size - (len(plaintext) % block_size))) 

def fixed_xor(b1: bytes, b2: bytes):
    return bytes([x ^ y for x, y in zip(b1,b2)])

def aes_ecb(pt: bytes, key: bytes):
    if len(pt) % 16 != 0:
        pt = pkcs7(pt)
    cipher = AES.new(key, AES.MODE_ECB)
    return cipher.encrypt(pt)

def aes_cbc(pt: bytes, key: bytes):
    if len(pt) % 16 != 0:
        pt = pkcs7(pt)

    iv = os.urandom(16)
    blocks = [pt[i:i+16] for i in range(0, len(pt), 16)]
    
    ct = []
    cipher = AES.new(key, AES.MODE_ECB)
    for i in range(len(blocks)):
        if i == 0:
            cti = fixed_xor(iv, blocks[i])
            ct.append(cipher.encrypt(cti))
            continue
        cti = fixed_xor(blocks[i-1], blocks[i])
        ct.append(cipher.encrypt(cti))
    return b"".join(ct)


def encryption_oracle(plaintext: str):
    salted_pt = salted(plaintext.encode())
    key = keygen_aes(16)
    mode = random.randrange(1,3)

    if mode == 1:
        ct = aes_ecb(salted_pt, key)
    else:
        ct = aes_cbc(salted_pt, key)
    return ct

def split_block(ciphertext: bytes, size = 16):
    blocks = []
    for i in range(0, len(ciphertext), size):
        blocks.append(ciphertext[i:i+size])
    return blocks

def check_repeated(block: list) -> int:
    block_length = len(block)
    uniq_block = len(set(block))
    diff = abs(block_length - uniq_block)
    if diff != 0:
        return diff
    return 0

pt = "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
ct = encryption_oracle(pt)
print(ct)

blocks = split_block(ct)
repeated = check_repeated(blocks)
if repeated > 0:
    print(f"Its ECB")
else:
    print("Its CBC")
