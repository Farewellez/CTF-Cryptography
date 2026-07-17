# Detect AES in ECB mode
def detect_aes_ecb(ciphertext: bytes) -> bool:
    blocks = [ciphertext[i:i+16] for i in range(0, len(ciphertext), 16)]
    if len(blocks) != len(set(blocks)):
        return True
    return False

with open("/mnt/d/my-kisah/crypto/1.cryptopals/files/8.txt") as f:
    for i,line in enumerate(f):    
        ct = bytes.fromhex(line)
        if detect_aes_ecb(ct):
            print(f"its ecb in line-{i}:\n{line}".strip())
