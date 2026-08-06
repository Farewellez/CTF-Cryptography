# You either know, XOR you don't
def repeating_key_xor(data: bytes, key: bytes) -> bytes:
    return bytes(bytearray([key[i%len(key)] ^ d for i, d in enumerate(data)]))

ct = bytes.fromhex("0e0b213f26041e480b26217f27342e175d0e070a3c5b103e2526217f27342e175d0e077e263451150104")
key = b"myXORkey"
pt = repeating_key_xor(ct, key)
print(pt.decode())