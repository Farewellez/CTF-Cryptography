# Implement repeating-key XOR
def repeating_xor(pt: bytes, key: bytes):
    ct = bytes(bytearray([p ^ key[i%len(key)] for i, p in enumerate(pt)]))
    return ct.hex()

pt = """
Burning 'em, if you ain't quick and nimble
I go crazy when I hear a cymbal
""".strip()
key = "ICE"

print(pt.encode())
ct = repeating_xor(pt.encode(), key.encode())
print(ct)
