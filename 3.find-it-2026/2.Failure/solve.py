from pwn import *
from z3 import *
import os

HOST = "challctf.find-it.id"
PORT = 8999

A = 0x04040404
B = 0x02000002
G = A ^ B
MASK = 0xffffffff

# ======================
# basic word helpers
# ======================

def words(x: bytes):
    return tuple(int.from_bytes(x[i:i+4], "big") for i in range(0, 12, 4))

def pack(ws):
    return b"".join((x & MASK).to_bytes(4, "big") for x in ws)

def xor_delta(p: bytes, d):
    w = list(words(p))
    return pack([w[i] ^ d[i] for i in range(3)])

# ======================
# cipher funcs, int side
# ======================

def rotl32(x, n):
    return ((x << n) | (x >> (32 - n))) & MASK

def rotl2(x):
    x &= 0xff
    return ((x << 2) | (x >> 6)) & 0xff

def sep_byte(w, idx):
    return (w >> (8 * idx)) & 0xff

def combine_bytes(b3, b2, b1, b0):
    return ((b3 & 0xff) << 24) | ((b2 & 0xff) << 16) | ((b1 & 0xff) << 8) | (b0 & 0xff)

def g_box(a, b, mode):
    return rotl2((a + b + mode) & 0xff)

def f_int(w):
    w = rotl32(w, 5)

    x0 = sep_byte(w, 0)
    x1 = sep_byte(w, 1)
    x2 = sep_byte(w, 2)
    x3 = sep_byte(w, 3)

    t0 = x2 ^ x3
    y1 = g_box(x0 ^ x1, t0, 1)
    y0 = g_box(x0, y1, 0)
    y2 = g_box(t0, y1, 0)
    y3 = g_box(x3, y2, 1)

    return combine_bytes(y3, y2, y1, y0) & MASK

def F_int(b, c, k):
    return f_int(c ^ f_int(b ^ k) ^ rotl32(k, 7))

def inv_round(st, k):
    a, b, c = st
    return ((c ^ F_int(a, b, k)) & MASK, a, b)

def inv_many(st, keys):
    for k in reversed(keys):
        st = inv_round(st, k)
    return st

# ======================
# Z3 side for one 32-bit key
# ======================

def z_rotl32(x, n):
    return RotateLeft(x, n)

def z_rotl2(x):
    return RotateLeft(x, 2)

def z_sep_byte(w, idx):
    return Extract(8 * idx + 7, 8 * idx, w)

def z_combine_bytes(b3, b2, b1, b0):
    return Concat(b3, b2, b1, b0)

def f_z3(w):
    w = z_rotl32(w, 5)

    x0 = z_sep_byte(w, 0)
    x1 = z_sep_byte(w, 1)
    x2 = z_sep_byte(w, 2)
    x3 = z_sep_byte(w, 3)

    t0 = x2 ^ x3
    y1 = z_rotl2((x0 ^ x1) + t0 + BitVecVal(1, 8))
    y0 = z_rotl2(x0 + y1)
    y2 = z_rotl2(t0 + y1)
    y3 = z_rotl2(x3 + y2 + BitVecVal(1, 8))

    return z_combine_bytes(y3, y2, y1, y0)

def F_z3(b, c, k):
    return f_z3(c ^ f_z3(b ^ k) ^ z_rotl32(k, 7))

def recover_key(eqs, name="k"):
    """
    eqs: [(b, c, b2, c2, diff), ...]
    solve F_k(b,c) ^ F_k(b2,c2) == diff
    """
    k = BitVec(name, 32)
    s = SolverFor("QF_BV")
    s.set("timeout", 30000)

    for b, c, b2, c2, d in eqs:
        s.add(
            F_z3(BitVecVal(b, 32), BitVecVal(c, 32), k)
            ^ F_z3(BitVecVal(b2, 32), BitVecVal(c2, 32), k)
            == BitVecVal(d & MASK, 32)
        )

    assert s.check() == sat, f"failed solving {name}"
    val = s.model().eval(k, model_completion=True).as_long()

    # verify with real int implementation
    for b, c, b2, c2, d in eqs:
        assert (F_int(b, c, val) ^ F_int(b2, c2, val)) == (d & MASK)

    log.success(f"{name} = {val:08x}")
    return val

# ======================
# remote oracle
# ======================

io = remote(HOST, PORT)

def enc(pt: bytes) -> bytes:
    io.sendlineafter(b">> ", b"1")
    io.sendlineafter(b"Input Plaintext (Hex): ", pt.hex().encode())
    line = io.recvline_contains(b"Encrypted:")
    return bytes.fromhex(line.decode().split("Encrypted:")[1].strip())

def claim(key: bytes):
    io.sendlineafter(b">> ", b"3")
    io.sendlineafter(b"Input Key (Hex): ", key.hex().encode())
    print(io.recvall(timeout=3).decode(errors="ignore"))

# ======================
# attack
# ======================

N = 8

# ---- recover k5, k4, k3 using delta (A,0,0)
pairs = []

for _ in range(N):
    p = os.urandom(12)
    q = xor_delta(p, (A, 0, 0))
    c = words(enc(p))
    d = words(enc(q))
    pairs.append((c, d))

eq5 = []
for c, d in pairs:
    eq5.append((c[0], c[1], d[0], d[1], c[2] ^ d[2]))

k5 = recover_key(eq5, "k5")

s5_pairs = []
for c, d in pairs:
    s5 = inv_round(c, k5)
    t5 = inv_round(d, k5)
    s5_pairs.append((s5, t5))

eq4 = []
for s5, t5 in s5_pairs:
    eq4.append((s5[0], s5[1], t5[0], t5[1], s5[2] ^ t5[2] ^ B))

k4 = recover_key(eq4, "k4")

s4_pairs = []
for s5, t5 in s5_pairs:
    s4 = inv_round(s5, k4)
    t4 = inv_round(t5, k4)
    s4_pairs.append((s4, t4))

eq3 = []
for s4, t4 in s4_pairs:
    eq3.append((s4[0], s4[1], t4[0], t4[1], s4[2] ^ t4[2] ^ A))

k3 = recover_key(eq3, "k3")

suffix = [k3, k4, k5]

# ---- recover k2 using delta (0,0,A)
pairs2 = []

for _ in range(N):
    p = os.urandom(12)
    q = xor_delta(p, (0, 0, A))

    s3 = inv_many(words(enc(p)), suffix)
    t3 = inv_many(words(enc(q)), suffix)

    pairs2.append((s3, t3))

eq2 = []
for s3, t3 in pairs2:
    eq2.append((s3[0], s3[1], t3[0], t3[1], s3[2] ^ t3[2] ^ A))

k2 = recover_key(eq2, "k2")

# ---- recover k1 using delta (0,A,G)
pairs1 = []

for _ in range(N):
    p = os.urandom(12)
    q = xor_delta(p, (0, A, G))

    s3 = inv_many(words(enc(p)), suffix)
    t3 = inv_many(words(enc(q)), suffix)

    s2 = inv_round(s3, k2)
    t2 = inv_round(t3, k2)

    pairs1.append((s2, t2))

eq1 = []
for s2, t2 in pairs1:
    eq1.append((s2[0], s2[1], t2[0], t2[1], s2[2] ^ t2[2] ^ A))

k1 = recover_key(eq1, "k1")

# ---- compute S1 for samples, leak w1 and w2
def get_s1(p: bytes):
    s3 = inv_many(words(enc(p)), suffix)
    s2 = inv_round(s3, k2)
    s1 = inv_round(s2, k1)
    return s1

samples = []

for _ in range(N):
    p = os.urandom(12)
    s1 = get_s1(p)
    samples.append((words(p), s1))

w1 = samples[0][1][0] ^ samples[0][0][1]
w2 = samples[0][1][1] ^ samples[0][0][2]

for p, s1 in samples:
    assert (s1[0] ^ p[1]) == w1
    assert (s1[1] ^ p[2]) == w2

log.success(f"w1 = {w1:08x}")
log.success(f"w2 = {w2:08x}")

# ---- recover k0 using random equations
eq0 = []

for _ in range(N):
    p = os.urandom(12)
    q = os.urandom(12)

    wp = words(p)
    wq = words(q)

    s1 = get_s1(p)
    t1 = get_s1(q)

    b1 = wp[1] ^ w1
    c1 = wp[2] ^ w2
    b2 = wq[1] ^ w1
    c2 = wq[2] ^ w2

    diff = s1[2] ^ t1[2] ^ wp[0] ^ wq[0]
    eq0.append((b1, c1, b2, c2, diff))

k0 = recover_key(eq0, "k0")

# ---- recover w0
p, s1 = samples[0]
w0 = p[0] ^ s1[2] ^ F_int(p[1] ^ w1, p[2] ^ w2, k0)

master_key = pack((w0, w1, w2))

log.success(f"master_key = {master_key.hex()}")

claim(master_key)