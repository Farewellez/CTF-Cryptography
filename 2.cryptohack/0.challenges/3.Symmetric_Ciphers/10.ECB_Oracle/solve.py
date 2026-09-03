import requests
from rich.console import Console

url = "https://aes.cryptohack.org/ecb_oracle"
console = Console()
printable = [ord(c) for c in "{|}_cryptoCYPTOetainshrdluETAINSHRDLU0123456789bfgjkmqvwxzBFGJKMQVWXZ!#$%&'()*+,-./:;<=>?@[\\]^`~"]

# https://www.ctfrecipes.com/cryptography/symmetric-cryptography/aes/mode-of-operation/ecb/ecb-oracle/challenge-example
def encrypt(payload: bytes):
    data = requests.get(f"{url}/encrypt/{payload.hex()}/")
    return data.json()["ciphertext"]

# payload = b"A"*32
# ciphertext = encrypt(payload)
# assert ciphertext[0:32] == ciphertext[32:64]
# print(f"EBC mode:")
# print(f"ciphertext (hex)  : {ciphertext}")

flag = b""
with console.status(f"FLAG: {flag}, Trying byte : ") as a:
    while len(flag) == 0 or flag[-1] != 125:
        for c in printable:
            c = c.to_bytes(1,'big')
            a.update(f"FLAG: {flag}, Trying byte : {c}")

            if len(flag) >= 16:
                payload = flag[-15:] + c + b'\x10' * (15 - (len(flag) % 16))
            else:
                payload = b'\x10' * (15 - len(flag)) + flag + c + b'\x10' * (15 - len(flag))
            cipher = encrypt(payload) 

            if cipher[0:32] == cipher[32 + (32 * (len(flag) // 16)) : 64 + (32 * (len(flag) // 16 ))]:
                # If it is, then the letter is found
                flag += c
                break
            
print(f"FLAG: {flag}")