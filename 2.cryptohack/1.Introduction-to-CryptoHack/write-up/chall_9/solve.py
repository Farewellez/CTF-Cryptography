# Favourite byte
def single_byte_xor(data: bytes, key: int):
    return bytes(bytearray([d ^ key for d in data]))

ct = "73626960647f6b206821204f21254f7d694f7624662065622127234f726927756d"
pt = bytes.fromhex(ct)

for k in range(256):
    cand = single_byte_xor(pt, k)
    if b"crypto" in cand:
        print(cand.decode())
        break