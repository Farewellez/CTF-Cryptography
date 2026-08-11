import requests

URL = "https://aes.cryptohack.org/flipping_cookie"

def get_cookie():
   return bytes.fromhex(requests.get(f"{URL}/get_cookie/").json()['cookie'])
def check_admin(cookie, iv):
   return requests.get(f"{URL}/check_admin/{cookie.hex()}/{iv.hex()}/").json()['flag']
def fixed_xor(b1, b2):
   return bytes([x ^ y for x,y in zip(b1,b2)])

ct = get_cookie()
iv = ct[:16]
target_iv = iv[0:11]
payload1 = b"admin=True;"
payload2 = b"admin=False"

spoofed_iv = fixed_xor(payload1, fixed_xor(payload2, iv)) + iv[11:]
data = check_admin(ct[16:], spoofed_iv)
print(data)