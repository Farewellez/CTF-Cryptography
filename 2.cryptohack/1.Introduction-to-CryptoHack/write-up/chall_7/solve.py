# XOR Starter
string = "label"
key = 13
ct = ""
for s in string.encode():
    ct += chr(s ^ key)
print(ct)