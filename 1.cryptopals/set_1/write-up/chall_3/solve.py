# Single-byte XOR cipher
def single_xor(k: int, ct: bytes) -> bytes:
    xord = bytes(bytearray([k ^ c for c in ct]))
    return xord

def scoring_english(cand: bytes) -> int:
    boost = ("ETAOIN SHRDLU".replace(" ","") + "ETAOIN SHRDLU".replace(" ","").lower())
    score = 0

    for c in cand:
        if chr(c) in boost:
            score += 3
        elif chr(c) == " ":
            score += 2
        elif chr(c).isalpha():
            score += 1
        else:
            score -= 1
    return score

def crack_single_xor(ct: bytes) -> list:
    candidate = []
    for i in range(256):
        pt = single_xor(i, ct)
        score = scoring_english(pt)
        candidate.append((pt, score))
    
    candidate.sort(key=lambda x: x[1], reverse=True)
    return candidate[:5]

ct = bytes.fromhex("1b37373331363f78151b7f2b783431333d78397828372d363c78373e783a393b3736")
cand = crack_single_xor(ct)[0][0]
print(cand.decode())
