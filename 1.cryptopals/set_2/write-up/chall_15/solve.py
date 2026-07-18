# PKCS#7 padding validation
def check_pkcs7(plaintext: str):
    ciphertext = plaintext.encode()
    padd_len = ciphertext[-1]
    bs = len(ciphertext)
    if padd_len == 0 or padd_len > bs:
        return "invalid padding"
    if ciphertext[-padd_len:] != bytes([padd_len]*padd_len):
        return "invalid padding"

    return ciphertext[:-padd_len].decode()

ct = "ICE ICE BABY\x04\x04\x04\x04"
is_valid = check_pkcs7(ct)
print(is_valid)

ct2 = "ICE ICE BABY\x05\x05\x05\x05"
is_valid2 = check_pkcs7(ct2)
print(is_valid2)
