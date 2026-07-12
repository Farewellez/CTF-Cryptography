# The Eepy Koala Write-up

## Challenge

- Category: Crypto
- Points: 199
- Files provided:
  - `enc.py`
  - `koala-enc.ppm`

## Given Encryption Script

```python
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
import os
import hashlib
import random

# W, H = 1920, 800
BLOCK_SIZE = 16

def permute(n, s):
    indices = list(range(n))
    state = s
    for i in range(n - 1, 0, -1):
        state = (state * 0x41c64e6d + 12345) & 0xFFFFFFFF
        j = (state ^ (state >> 16)) % (i + 1)
        indices[i], indices[j] = indices[j], indices[i]
    return indices

def main():
    with open("plain.ppm", "rb") as f:
        header = f.readline() + f.readline() + f.readline()
        pixel_data = f.read()
        
    secret_seed = random.randint(0, 65535)
    seed_bytes = secret_seed.to_bytes(2, 'big')
    key = hashlib.sha256(seed_bytes).digest()[:16]
    cipher = AES.new(key, AES.MODE_ECB)

    raw = pad(pixel_data, BLOCK_SIZE)
    blocks = [cipher.encrypt(raw[i:i+BLOCK_SIZE]) for i in range(0, len(raw), BLOCK_SIZE)]
    
    n = len(blocks)
    mapping = permute(n, secret_seed)
    
    shuffled_blocks = [None] * n
    for i, pos in enumerate(mapping):
        shuffled_blocks[pos] = blocks[i]
    
    with open("koala-enc.ppm", "wb") as f:
        f.write(header + b"".join(shuffled_blocks))

if __name__ == "__main__":
    main()
```

## Analysis

The challenge uses two protections:

1. AES-ECB encryption for each 16-byte block.
2. A deterministic block permutation generated from the same 16-bit seed.

The weak point is the tiny seed space:

- `secret_seed` is only in `[0, 65535]`
- The AES key is directly derived from that seed
- The permutation also depends on the same seed

So in principle we can brute-force all possible seeds.

## Important Observation

The encrypted file is a PPM image with:

- Width = `1920`
- Height = `800`
- 3 bytes per pixel

So the raw pixel size is:

```text
1920 * 800 * 3 = 4,608,000 bytes
```

Since AES block size is 16:

```text
4,608,000 mod 16 = 0
```

That means PKCS#7 padding adds a full extra block:

```text
10 10 10 10 10 10 10 10 10 10 10 10 10 10 10 10
```

This gives us a known plaintext block.

## Why This Makes Brute Force Easy

We do not need to fully decrypt the image for every seed.

We only need to find which ciphertext block corresponds to the last plaintext block, because that last plaintext block is known in advance: `0x10 * 16`.

From the permutation function:

```python
for i in range(n - 1, 0, -1):
    state = (state * 0x41c64e6d + 12345) & 0xFFFFFFFF
    j = (state ^ (state >> 16)) % (i + 1)
    indices[i], indices[j] = indices[j], indices[i]
```

The position of the last plaintext block is determined in the very first loop iteration, when `i = n - 1`.

So for each candidate seed:

1. Compute one LCG step.
2. Compute the position of the last block.
3. Decrypt only that single ciphertext block with the AES key derived from the seed.
4. Check whether it equals `0x10 * 16`.

If yes, the seed is correct.

This reduces the brute force to only one AES block decryption per seed.

## Seed Recovery Script

```python
from pathlib import Path
import hashlib
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

BLOCK = 16
A = 0x41c64e6d
C = 12345

data = Path("koala-enc.ppm").read_bytes()
parts = data.split(b"\n", 3)
body = parts[3]
blocks = [body[i:i+BLOCK] for i in range(0, len(body), BLOCK)]
n = len(blocks)

target = bytes([16]) * 16

for seed in range(65536):
    state = (seed * A + C) & 0xFFFFFFFF
    pos = (state ^ (state >> 16)) % n

    key = hashlib.sha256(seed.to_bytes(2, "big")).digest()[:16]
    cipher = Cipher(algorithms.AES(key), modes.ECB())
    dec = cipher.decryptor()
    pt = dec.update(blocks[pos]) + dec.finalize()

    if pt == target:
        print("seed =", seed)
        break
```

Output:

```text
seed = 45405
```

## Full Decryption

After recovering the seed, we rebuild the permutation, undo the shuffle, decrypt all blocks, and remove PKCS#7 padding.

```python
from pathlib import Path
import hashlib
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

BLOCK = 16
SEED = 45405
A = 0x41c64e6d
C = 12345

def permute(n, s):
    indices = list(range(n))
    state = s
    for i in range(n - 1, 0, -1):
        state = (state * A + C) & 0xFFFFFFFF
        j = (state ^ (state >> 16)) % (i + 1)
        indices[i], indices[j] = indices[j], indices[i]
    return indices

data = Path("koala-enc.ppm").read_bytes()
parts = data.split(b"\n", 3)
header = b"\n".join(parts[:3]) + b"\n"
body = parts[3]

blocks = [body[i:i+BLOCK] for i in range(0, len(body), BLOCK)]
n = len(blocks)
mapping = permute(n, SEED)

ordered = [None] * n
for i, pos in enumerate(mapping):
    ordered[i] = blocks[pos]

key = hashlib.sha256(SEED.to_bytes(2, "big")).digest()[:16]
cipher = Cipher(algorithms.AES(key), modes.ECB())
dec = cipher.decryptor()
plain = dec.update(b"".join(ordered)) + dec.finalize()

pad_len = plain[-1]
plain = plain[:-pad_len]

Path("koala-restored.ppm").write_bytes(header + plain)
print("restored")
```

## Result

The restored image contains the flag:

```text
FindITCTF{w0W_sUch_4n_4W3s0m3_k0aL4}
```

## Final Flag

```text
FindITCTF{w0W_sUch_4n_4W3s0m3_k0aL4}
```

