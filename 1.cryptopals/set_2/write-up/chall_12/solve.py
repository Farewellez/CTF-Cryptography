# Byte-at-a-time ECB decryption (Simple)
import os
import base64
from Crypto.Cipher import AES

def keygen_aes(keysize: int):
    return os.urandom(keysize)

KEY = keygen_aes(16)

def salted(plaintext: bytes): return plaintext + base64.b64decode("Um9sbGluJyBpbiBteSA1LjAKV2l0aCBteSByYWctdG9wIGRvd24gc28gbXkgaGFpciBjYW4gYmxvdwpUaGUgZ2lybGllcyBvbiBzdGFuZGJ5IHdhdmluZyBqdXN0IHRvIHNheSBoaQpEaWQgeW91IHN0b3A/IE5vLCBJIGp1c3QgZHJvdmUgYnkK")

def pkcs7(plaintext: bytes, block_size = 16): return plaintext + (bytes([(block_size - (len(plaintext) % block_size))]) * (block_size - (len(plaintext) % block_size))) 

def fixed_xor(b1: bytes, b2: bytes):
    return bytes([x ^ y for x, y in zip(b1,b2)])

def aes_ecb(pt: bytes, key: bytes):
    if len(pt) % 16 != 0:
        pt = pkcs7(pt)
    cipher = AES.new(key, AES.MODE_ECB)
    return cipher.encrypt(pt)

def ecb_oracle(plaintext: bytes):
    salted_pt = salted(plaintext)
    key = KEY
    ct = aes_ecb(salted_pt, key)
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

def find_block_size():
    base_len = 0
    block_size = 0
    for i in range(0, 64):
        payloads = b'A'*i
        ct = ecb_oracle(payloads)
        if i == 0:
            base_len += len(ct)
            continue
        if base_len < len(ct):
            block_size = len(ct) - base_len
            break
    return block_size

def check_ecb(block_size: int):
    pt = b"A"*block_size*2
    ct = ecb_oracle(pt)
    blocks = split_block(ct)
    repeated = check_repeated(blocks)

    if repeated > 0:
        return True
    return False

def break_oracle(block_size: int):
    known_pt = b""
    while True:
        padding_len = (block_size - 1) - (len(known_pt) % block_size)
        prefix = b'A'*padding_len
        target_block = len(known_pt) // block_size

        dictionary = {}
        for i in range(256):
            payloads = prefix + known_pt + bytes([i])
            ct = ecb_oracle(payloads)
            dict_key = split_block(ct, block_size)[target_block]
            dictionary[dict_key] = bytes([i])
        
        ct_short = ecb_oracle(prefix)
        target_ct_block = split_block(ct_short, block_size)[target_block]

        if target_ct_block in dictionary:
            known_pt += dictionary[target_ct_block]
        else:
            break
    return known_pt


block_size = find_block_size()
print(f"block size: {block_size}")
ecb = check_ecb(block_size)
if ecb:
    print("ECB")

pt = break_oracle(block_size)
print(f"plaintext: \n{pt.decode(errors="ignore")}")
