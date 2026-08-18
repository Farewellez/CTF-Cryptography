ct = "73626960647f6b206821204f21254f7d694f7624662065622127234f726927756d"
for i in range(256):
    pt = bytes([x ^ i for x in bytes.fromhex(ct)])
    if b"crypto" in pt:
        print(pt)
        break