# ECB cut-and-paste
import os
from Crypto.Cipher import AES

KEY = os.urandom(16)

def pkcs7(plaintext: bytes, block_size = 16): return plaintext + (bytes([(block_size - (len(plaintext) % block_size))]) * (block_size - (len(plaintext) % block_size))) 

def profile_for(profile: str):
    data = {}
    data["email"] = profile
    data["uid"] = 10
    data["role"] = "user"
    profile = profile.replace("&", "").replace("=", "")

    encoded_data = ""
    for key in data:
        encoded_data += f"{key}={data[key]}"
        encoded_data += "&"

    return encoded_data[:-1]

def profile_encrypt(encoded_profile: bytes):
    encoded_profile = pkcs7(encoded_profile)
    key = KEY
    cipher = AES.new(key, AES.MODE_ECB)
    ct = cipher.encrypt(encoded_profile)
    return ct

def profile_decrypt(encrypted_profile: bytes):
    key = KEY
    cipher = AES.new(key, AES.MODE_ECB)
    pt = cipher.decrypt(encrypted_profile)
    pad_len = pt[-1]
    pt = pt[:-pad_len].split(b"&")
    cookies = {}
    for data in pt:
        split_pt = data.split(b"=")
        cookies[split_pt[0].decode()] = split_pt[1].decode()
    return cookies

# gmail = profile_for("foo@bar.com")
# enc_profile = profile_encrypt(gmail.encode())
# dec_profile = profile_decrypt(enc_profile)
# print(f"email            : {gmail}")
# print(f"profile          : {enc_profile}")
# print(f"decrypted profile: {dec_profile}")

# trying exploit 1
# email=  | 6
# [email] | x
# &uid=   | 5
# [uid]   | 2
# &role=  | 6
# total = 19 + x
# x + 19 ≡ 0 (mod 16)
# x = 13
# email=&uid=10&role=

# collect ciphertext 1
# print()
spoof1 = 'a'*13
gmail_spoof1 = profile_for(spoof1)
enc_spoof1 = profile_encrypt(gmail_spoof1.encode())
dec_spoof1 = profile_decrypt(enc_spoof1)
# print(f"email            : {gmail_spoof1}")
# print(f"profile          : {enc_spoof1}")
# print(f"decrypted profile: {dec_spoof1}")
# print(gmail_spoof1[:32])

# print()
# trying exploit 2
# email=  | 6
# [email] | a*10 = 10
# admin   | 5
# padd    | y
# y = 11 pkcs#7
spoof2 = 'a'*10 + "admin" + '\x0b'*11
gmail_spoof2 = profile_for(spoof2)
enc_spoof2 = profile_encrypt(gmail_spoof2.encode())
dec_spoof2 = profile_decrypt(enc_spoof2)
# print(f"email            : {gmail_spoof2.encode()}")
# print(f"profile          : {enc_spoof2}")
# print(f"decrypted profile: {dec_spoof2}")
# print(gmail_spoof2[16:32].encode())

# concenate
admin = enc_spoof2[16:32]
# print(len(gmail_spoof2[16:32].encode()))
final_spoof = enc_spoof1[:32] + admin
# print(len(final_spoof)%16)
decrypt_spoof = profile_decrypt(final_spoof)
print(decrypt_spoof)
