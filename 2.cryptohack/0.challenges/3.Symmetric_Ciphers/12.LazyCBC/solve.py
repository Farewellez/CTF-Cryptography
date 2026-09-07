import requests
import re

URL = "https://aes.cryptohack.org/lazy_cbc/"

class Remote:
    def __init__(self, param):
        self.param = param
        self.base_url = URL
        self.session = requests.Session()

    def _get_json(self, endpoint):
        url = f"{URL}{endpoint}"
        response = self.session.get(url)
        return response.json()

    def encrypt(self):
        plaintext = self.param
        ciphertext = self._get_json(f"encrypt/{plaintext}/")["ciphertext"]
        return ciphertext

    def recieve(self):
        ciphertext = self.param
        pt = self._get_json(f"receive/{ciphertext}/")
        return pt

    def get_flag(self):
        key = self.param
        data = self._get_json(f"get_flag/{key}/")
        return data


def fixed_xor(p1,p2):
    return bytes([x ^ y for x,y in zip(p1,p2)])

# https://crypto.stackexchange.com/questions/16161/problems-with-using-aes-key-as-iv-in-cbc-mode
pt = 'A'*(16*3)
Rciphertext = Remote(pt.encode().hex())
ciphertext = Rciphertext.encrypt()
print(f"original ciphertext (hex)  : {ciphertext}")
print(f"original ciphertext (bytes): {bytes.fromhex(ciphertext)}")

block_cipher = [bytes.fromhex(ciphertext)[i:i+16] for i in range(0,len(bytes.fromhex(ciphertext)),16)]
C0 = block_cipher[0]
C1 = b'\x00'*16
C2 = block_cipher[0]
mC = C0 + C1 + C2

Rdata = Remote(mC.hex())
data = Rdata.recieve()["error"]
if data:
    P = re.search(r'[0-9a-fA-F]{2,}', data).group()

block_p = [bytes.fromhex(P)[i:i+16] for i in range(0,len(bytes.fromhex(P)),16)]
P0 = block_p[0]
P2 = block_p[2]
key = fixed_xor(P0, P2)
assert len(key) == 16, "key length != 16"
print(F"KEY: {key.hex()}")

Rflag = Remote(key.hex())
flag = Rflag.get_flag()["plaintext"]
print(f"FLAG: {bytes.fromhex(flag)}")