# Break repeating-key XOR
import base64

def fixed_xor(b1: bytes, b2: bytes):
    if len(b1) - len(b2) != 0:
        raise Exception("parameters must have same length...")
    return bytes(bytearray([x ^ y for x, y in zip(b1, b2)]))

def hamming_distance(b1: bytes, b2: bytes):
    xord = fixed_xor(b1, b2)
    return int.from_bytes(xord, "big").bit_count()

def repeating_key_xor(ciphertext: bytes, key: bytes): return bytes(bytearray([c ^ key[i%len(key)] for i, c in enumerate(ciphertext)]))

def guess_keysize(ciphertext: bytes, low = 2, high = 40):
    result = []

    for ks in range(low, high):
        chunks = [ciphertext[i:i+ks] for i in range(0, len(ciphertext), ks)][:8]
        scores = []
        for i1 in range(0,len(chunks)-1):
            for i2 in range(i1+1,len(chunks)):
                if len(chunks[i1]) != ks or len(chunks[i2]) != ks:
                    continue
                scores.append(hamming_distance(chunks[i1], chunks[i2])/ks)
        if not scores:
            continue
        avg_score = sum(scores)/len(scores)
        result.append((ks, avg_score))
    
    result.sort(key=lambda x: x[1])
    return [ks for ks,_ in result]

def single_byte_xor(ciphertext: bytes, key: int): return bytes(bytearray([c ^ key for c in ciphertext]))

def letter_frequency_scoring(word: bytes):
    boost = b"etaoinshrdlu ETAOINSHRDLU"
    minus = b"~@#$%^&*{}[]|"
    score = 0

    for c in word:
        if c in b"\n\t\r":
            score += 1
        elif c < 32 or c > 126:
            score -= 20
            continue

        if c in boost:
            score += 3
        if c == ord(" "):
            score += 5
        if chr(c).isalpha():
            score += 1
        if c in minus:
            score -= 2
    return score        
    
def crack_single_xor(ciphertext: bytes):
    candidate = None
    for i in range(256):
        xord = single_byte_xor(ciphertext, i)
        score = letter_frequency_scoring(xord)
        if candidate is None or score > candidate[1]:
            candidate = (i, score)
    
    return candidate

def recover_key(ciphertext: bytes, keysize: int):
    blocks_ct = [ciphertext[i:i+keysize] for i in range(0, len(ciphertext), keysize)]
    transpose = []

    for i in range(keysize):
        tmp = []
        for block in blocks_ct:
            if i < len(block):
                tmp.append(block[i])
        
        transpose.append(bytes(tmp))
    
    key = b""
    for k in transpose:
        cand_key = crack_single_xor(k)
        key += bytes([cand_key[0]])
    return key


# test1 = b"this is a test"
# test2 = b"wokka wokka!!!"
# hd = hamming_distance(test1, test2)
# print(hd)

with open("/mnt/d/my-kisah/crypto/1.cryptopals/files/6.txt") as f:
    buffer = "".join(line.strip() for line in f)

ct = base64.b64decode(buffer)
ks = guess_keysize(ct)

for s in ks[:1]:
    cand_ks = recover_key(ct, s)
    pt = repeating_key_xor(ct, cand_ks)
    print(pt.decode(errors="ignore"))
