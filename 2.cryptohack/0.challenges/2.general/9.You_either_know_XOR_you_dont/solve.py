ct = "0e0b213f26041e480b26217f27342e175d0e070a3c5b103e2526217f27342e175d0e077e263451150104"
kp = "crypto{"

key = ""
for i in range(len(kp)):
    key += chr(bytes.fromhex(ct)[i] ^ ord(kp[i]))

print(key) # we got myXORke, so we know the last character is "y" -> key = myXORkey, lets try it

key = "myXORkey"
pt = ""
for i, c in enumerate(bytes.fromhex(ct)):
    pt += chr(c ^ ord(key[i % len(key)]))

print(pt)