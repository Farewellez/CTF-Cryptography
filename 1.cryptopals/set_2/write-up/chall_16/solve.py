# CBC bitflipping attacks
import os
import re
from Crypto.Cipher import AES

BS = 16
KEY = os.urandom(BS)

def salted(plaintext: str): return "comment1=cooking%20MCs;userdata=" + plaintext + ";comment2=%20like%20a%20pound%20of%20bacon"

def pkcs7(plaintext: bytes): return plaintext + (bytes([BS - (len(plaintext) % BS)]) * (BS - (len(plaintext) % BS)))

def fixed_xor(pt: bytes, key: bytes):  assert len(pt) == len(key), "pt and key must have same length!"; return bytes([p ^ k for p, k in zip(pt, key)])

def cbc_oracle(plaintext: str):
    IV = os.urandom(BS)
    plaintext = re.sub(r"[;=]", "", plaintext)
    plaintext = salted(plaintext)

    pt = pkcs7(plaintext.encode())
    blocks = [pt[i:i+16] for i in range(0, len(pt), 16)]
    cipher = AES.new(KEY, AES.MODE_ECB)

    for i in range(len(blocks)):
        if i == 0:
            xord = fixed_xor(blocks[i], IV)
        else:
            xord = fixed_xor(blocks[i - 1], blocks[i])
        ct = cipher.encrypt(xord)
        blocks[i] = ct
    
    return IV + b"".join(blocks)

def cbc_decrypt(ciphertext: bytes):
    iv = ciphertext[:16]
    ct_raw = ciphertext[16:]

    blocks = [ct_raw[i:i+16] for i in range(0, len(ct_raw), 16)]
    cipher = AES.new(KEY, AES.MODE_ECB)
    pt = b""
    for i in range(len(blocks)):
        ct = cipher.decrypt(blocks[i])
        if i == 0:
            xord = fixed_xor(ct, iv)
        else:
            xord = fixed_xor(blocks[i - 1], ct)
        pt += xord
    
    # print([pt[i:i+16] for i in range(0, len(pt), 16)])
    splitted = pt.split(b';')
    if b'admin=true' in splitted:
        return True
    return False

payload = 'a'*16
pt = payload + ":admin:true:"
ct = cbc_oracle(pt)
dec_pt = cbc_decrypt(ct)

iv = ct[:16]
test_block = [ct[i:i+16] for i in range(16, len(ct), 16)]
# print()
# for block in test_block:
#     print(block)

# print()
# print(dec_pt)

# block0: comment1=cooking
# block1: %20MCs;userdata=
# block2: aaaaaaaaaaaaaaaa
# block3: :admin:true:;com -> 0, 6, 11
# block4: ment2=%20like%20
# ...
# ct0 = block0 xor iv
# ct1 = block1 xor ct0
# ct2 = block2 xor ct1
# ct3 = block3 xor ct2 -> payload
# somehow in decrypt function
# pt1 = ct0 xor iv
# pt2 = ct1 xor ct0
# pt3 = ct2 xor ct1
# so if we try modifying ct2 output, it will affect on pt3

# ct2 = 16*2 = 32
modif_ct = bytearray(test_block[2])
modif_ct[0] ^= 0x1
modif_ct[6] ^= 0x7
modif_ct[11] ^= 0x1
test_block[2] = bytes(modif_ct)

payload_final = iv + b"".join(test_block)
decrypted_admin = cbc_decrypt(payload_final)
print(decrypted_admin)
