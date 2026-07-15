# Fixed XOR
def fixed_xor(h1: str, h2: str) -> str:
    if len(h1) - len(h2) != 0:
        return "parameters must have same lenght..."
    
    ct = [hex(x ^ y)[2:] for x, y in zip(bytes.fromhex(h1), bytes.fromhex(h2))]
    return "".join(ct)

p1 = "1c0111001f010100061a024b53535009181c"
p2 = "686974207468652062756c6c277320657965"
xor_p1_p2 = fixed_xor(p1, p2)
print(xor_p1_p2)
