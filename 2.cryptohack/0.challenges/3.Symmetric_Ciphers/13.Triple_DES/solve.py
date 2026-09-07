import requests
import time
from Crypto.Cipher import DES3
from Crypto.Random import get_random_bytes

base_url = "https://aes.cryptohack.org/triple_des"
session = requests.session()
bs = 8

def get_flag(key, ct):
    data = session.get(f"{base_url}/encrypt/{key}/{ct}/")
    return data.json()

def encrypt(key):
    data = session.get(f"{base_url}/encrypt_flag/{key}/")
    return data.json()
    # try:
    #     ct = data.json()["ciphertext"]
    #     return ct
    # except KeyError:
    #     return data.json()["error"]

# awalnya udah mau nerapin https://crypto.stackexchange.com/questions/91519/why-is-this-des-key-considered-weak tapi aku coba semua 0 dan semua 1 itu gaditerima:
# k1: b'\x00\x00\x00\x00\x00\x00\x00\x00'
# k2: b'\x01\x01\x01\x01\x01\x01\x01\x01'

# weak ciphertext: {'error': 'Triple DES key degenerates to single DES'}
# {'error': 'non-hexadecimal number found in fromhex() arg at position 0'}

# lalu coba cek ini https://www.scribd.com/document/477441790/weak-and-Semi-weak-keys-in-DES
# dari situ dapat, bukan cuma weak keys, tapi semi weak keys yang bisa bekerja

k1 = bytes([1])*8
k2 = bytes([254])*8
print(f"k1: {k1}")
print(f"k2: {k2}")
print()
key = k1 + k2 + k1

weak_ct = encrypt(key.hex())["ciphertext"]
print(f"weak ciphertext: {weak_ct}")

flag = get_flag(key.hex(), weak_ct)["ciphertext"]
print(bytes.fromhex(flag))