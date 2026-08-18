pt = "label"
ct = bytes([x ^ 13 for x in pt.encode()])
flag = "crypto{" + ct.decode() + "}"
print(flag)