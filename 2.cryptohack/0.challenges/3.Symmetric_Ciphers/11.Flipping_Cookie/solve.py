import requests
from datetime import datetime,timedelta

url = "https://aes.cryptohack.org/flipping_cookie"

def fixed_xor(b1,b2):
    return bytes([x ^ y for x,y in zip(b1,b2)])

def cookie():
    data = requests.get(f"{url}/get_cookie/")
    ciphertext = data.json()["cookie"]
    return ciphertext

def check_admin(cookie, iv):
    data = requests.get(f"{url}/check_admin/{cookie.hex()}/{iv.hex()}/")
    try:
        flag = data.json()["flag"]
        return flag
    except KeyError:
        return data.json()["error"]

# expires_at = (datetime.today() + timedelta(days=1)).strftime("%s")
# cookie = f"admin=False;expiry={expires_at}".encode()
# print(expires_at, len(expires_at))
# print(cookie, len(cookie))

cookies = bytes.fromhex(cookie())
iv = cookies[:16]
ciphertext = cookies[16:]

# iviviviviviviviv block 0
# admin=False;expi block 1
# ry=1788576414PPP block 2

# encrypted:
# block ct 0: block 1 XOR iv and then ENC(key, block 1) 
# block ct 1: block 2 XOR block 1 and then ENC(key, block 2)

# decrypted:
# block pt 1: DEC(key, block ct 1) XOR iv
# block pt 2: DEC(key, block ct 2) XOR block ct 1

# equation 1:
# block pt 1 = DEC(key, block ct 1) XOR iv
# DEC(key, block ct 1) = block pt 1 XOR  XOR iv

# equation 2:
# new block pt 1 = DEC(key, block ct 1) XOR modified iv
# new block pt 1 = block pt 1 XOR iv XOR modified iv
# modified iv = new block pt 1 XOR block pt 1 XOR iv

new_block_pt_1 = b"admin=True;aexpi"
ori_block_pt_1 = b"admin=False;expi"
modified_iv = fixed_xor(fixed_xor(new_block_pt_1, ori_block_pt_1), iv)

flag = check_admin(ciphertext, modified_iv)
print(flag)