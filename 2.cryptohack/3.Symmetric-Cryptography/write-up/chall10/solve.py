import requests
from Crypto.Util.Padding import unpad

URL = "https://aes.cryptohack.org/ecb_oracle"
BS = 16
SESSION = requests.session()

def encrypt(plaintext: bytes):
    r = SESSION.get(f"{URL}/encrypt/{plaintext.hex()}/")
    data = r.json()['ciphertext']
    return bytes.fromhex(data)

def split_blocks(ciphertext):
    return [ciphertext[i:i+BS] for i in range(0,len(ciphertext),BS)]

known_pt = b""
common_chars = (b"etaoinshrdlugwyfmpbkvjxqz_{}ETAOINSHRDLUGWYFMPBKVJXQZ0123456789")

candidates = bytearray(common_chars)
for i in range(256):
    if i not in candidates:
        candidates.append(i)

while True:
    pad_len = (BS - 1) - (len(known_pt) % BS)

    if pad_len == 0:
        prefix = b'A' * BS
    else:
        prefix = b'A' * pad_len

    target_block = (len(prefix) + len(known_pt)) // BS

    ct_ori = encrypt(prefix)
    block_ori = split_blocks(ct_ori)[target_block]

    found = False
    for c in candidates:
        payload = prefix + known_pt + bytes([c])
        ct = encrypt(payload)
        block_ct = split_blocks(ct)[target_block]

        if block_ct == block_ori:
            known_pt += bytes([c])
            print(known_pt)
            found = True
            break
        
    if not found or known_pt.endswith(b"}"):
        break

print(f"Flag: {known_pt}")