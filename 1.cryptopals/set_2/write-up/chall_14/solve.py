# Byte-at-a-time ECB decryption (Harder)
import os
import random
import base64
from Crypto.Cipher import AES

KEY = os.urandom(16); BLOCK_SIZE = 16
count = random.randrange(5,11)
PREFIX = os.urandom(count)

def salted_prefix(plaintext: bytes): return PREFIX + plaintext  

def salted_target(plaintext: bytes): return plaintext + base64.b64decode("Um9sbGluJyBpbiBteSA1LjAKV2l0aCBteSByYWctdG9wIGRvd24gc28gbXkgaGFpciBjYW4gYmxvdwpUaGUgZ2lybGllcyBvbiBzdGFuZGJ5IHdhdmluZyBqdXN0IHRvIHNheSBoaQpEaWQgeW91IHN0b3A/IE5vLCBJIGp1c3QgZHJvdmUgYnkK")

def pkcs7(plaintext: bytes, blocksize = BLOCK_SIZE): return plaintext + (bytes([blocksize - (len(plaintext) % blocksize)]) * (blocksize - (len(plaintext) % blocksize)))  

def ecb_oracle(plaintext: bytes, key = KEY):
    plaintext = salted_prefix(plaintext)
    plaintext = salted_target(plaintext)
    plaintext = pkcs7(plaintext)

    cipher = AES.new(key, AES.MODE_ECB)
    ct = cipher.encrypt(plaintext)
    return ct
# pt = b"A"
# print(ecb_oracle(pt))

# looking for block size
def finding_block_size():
    base_len = 0
    block_size = 0

    for i in range(0, 64):
        pt = b'A'*i
        ct = ecb_oracle(pt)
        if i == 0:
            base_len = len(ct)
            continue
        if base_len < len(ct):
            block_size = len(ct) - base_len
            break

    return block_size

def split_blocks(ciphertext: bytes, block_size: int): return [ciphertext[i:i+16] for i in range(0,len(ciphertext),block_size)]

def check_repeated(block_ori: list[bytes], block_unique: set[bytes]):
    for i, b in enumerate(block_unique):
        if block_ori[i] != b:
            return i

def check_ecb(block_size: int):
    pt = b"a"
    for i in range(0,100):
        ct = ecb_oracle(pt*i)
        blocks = split_blocks(ct, block_size)
        unique = set(blocks)
        if len(blocks) != len(unique):
            return (ct,check_repeated(blocks, unique),True,i)
    
    return (b"0",0,False, 0)

block_size = finding_block_size()
repeated = check_ecb(block_size)
blocks = split_blocks(repeated[0], block_size)
repeated_blocks = len(blocks) - len(set(blocks)) + 1
residue = abs(repeated[3] - (repeated_blocks*block_size))
print(f"ECB: {repeated[2]} found repeated at block: {repeated[1] + 1}")
print(f"total same block: {repeated_blocks}")
print(f"payload length  : {repeated[3]}")
print(f"residue         : {residue}")
print(f"blocks ct       : {blocks}")

payload = b'a'*residue

known_pt = b""
while True:
    pad_len = (block_size - 1) - (len(known_pt) % block_size)
    pad_align = b"A" * pad_len
    target_block_idx = (repeated[1] + 1) + len(known_pt) // block_size

    sentence_cipher = {}
    for w in range(256):
        cand = pad_align + known_pt + bytes([w])
        ct = ecb_oracle(payload + cand)
        dict_key = split_blocks(ct, block_size)[target_block_idx]
        sentence_cipher[dict_key] = bytes([w])

    ct_short = ecb_oracle(payload + pad_align)
    target_ct_block = split_blocks(ct_short, block_size)[target_block_idx]

    if target_ct_block in sentence_cipher:
        known_pt += sentence_cipher[target_ct_block]
    else:
        break 
print(known_pt.decode())
