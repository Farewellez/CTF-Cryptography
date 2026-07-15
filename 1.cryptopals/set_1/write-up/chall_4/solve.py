# Detect single-character XOR
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

def crack_single_xor(ct: bytes) -> list[bytes]:
    candidate = []
    for i in range(256):
        pt = single_xor(i, ct)
        score = scoring_english(pt)
        candidate.append((pt, score))
    
    candidate.sort(key=lambda x: x[1], reverse=True)
    return candidate[:1]

with open("/mnt/d/my-kisah/crypto/1.cryptopals/files/4.txt") as f:
    buffer = f.readlines()

candidate = []
for ct in buffer:
    pt = crack_single_xor(bytes.fromhex(ct.strip()))[0][0]
    score = scoring_english(pt)
    candidate.append((pt, score))
    candidate.sort(key=lambda x: x[1], reverse=True)

print(candidate[0][0].decode().strip())
