import requests

URL = "https://aes.cryptohack.org/ecbcbcwtf"
BS = 16
SESSION = requests.session()

def encrypt():
    r = SESSION.get(f"{URL}/encrypt_flag/")
    data = r.json()['ciphertext']
    return bytes.fromhex(data)

def decrypt(ciphertext):
    r = SESSION.get(f"{URL}/decrypt/{ciphertext}/")
    data = r.json()
    pt = data['plaintext']
    return bytes.fromhex(pt)  

def fixed_xor(c1,c2):
    return bytes([x ^ y for x,y in zip(c1,c2)])

ct = encrypt()
known_pt = b""
block_ct = [ct[i:i+BS] for i in range(0,len(ct),BS)]

for i in range(0,len(block_ct)-1):
    # print(block_ct[i+1].hex())
    cn = decrypt(block_ct[i+1].hex())
    xord = fixed_xor(block_ct[i], cn)
    known_pt += xord

print(known_pt.decode())