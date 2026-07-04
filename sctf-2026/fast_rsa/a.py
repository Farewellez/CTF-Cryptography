import math
from Crypto.Util.number import long_to_bytes

def continue_fraction(e, N):
    coeffs = []
    while N:
        a = e // N
        coeffs.append(a)
        e, N = N, e - (a * N)
    return coeffs

def convergent(coeffs):
    p2, p1 = 0, 1
    q2, q1 = 1, 0
    out = []

    for a in coeffs:
        p = a * p1 + p2
        q = a * q1 + q2
        out.append((p, q))
        p2, p1 = p1, p
        q2, q1 = q1, q
    return out

def is_perfect_square(n: int):
    if n < 0:
        return None
    root = math.isqrt(n)
    return root if root * root == n else None

def main(N: int, e: int, prefix: int, unknown_bits: int, max_coeff: int = 1 << 12):
    # return value coefficient and convergent
    coeffs = continue_fraction(e, N)
    convs = convergent(coeffs)

    # boundary
    low = prefix << unknown_bits
    high = ((prefix + 1) << unknown_bits) - 1

    for i in range(len(convs) - 1):
        k0, d0 = convs[i]
        k1, d1 = convs[i + 1]

        # d can lie slightly beyond the classic Wiener range, so search
        # small combinations of adjacent convergent denominators.
        for r in range(max_coeff + 1):
            base_d = r * d1
            if base_d > high:
                break

            s_min = max(0, (low - base_d + d0 - 1) // d0)
            s_max = min(max_coeff, (high - base_d) // d0)
            if s_min > s_max:
                continue

            for s in range(s_min, s_max + 1):
                d = base_d + s * d0
                k = r * k1 + s * k0
                if k == 0 or (e * d - 1) % k != 0:
                    continue

                phi = (e * d - 1) // k
                b = N - phi + 1
                root = is_perfect_square(b * b - 4 * N)
                if root is None:
                    continue

                p = (b + root) // 2
                q = (b - root) // 2
                if p * q == N:
                    return d, p, q, k, i, r, s

    return None

# variables
N = 123436627937364220533270481649818241453723967384115317594580901509579002824492262533794630377279193802667379328735965163616334782488239489087324009223510505963533224573946190880685234990343308688615124347997748068891941544581957313716048480814498261130855640228654079732420165464995937087159234466591205031751
e = 52286779493719729111591951649018041120591431350255885880577954404417007096031542111805947925585000343367614092261219489270418623551496489397138684909838323937877627127780914093840297043462429076058522270894279052896963585381556897521605273988530094327726762243365869008195095849872139679930482993327784210855
C = 18307439754530257973400778807902998716623475594653775301290303045002722390993302047608662285458447774397358610645344936545249766330424835416841280732941976558802246418405394883748778049855176308710527927843514145576183854220758621096505224039138515443926112102198919593418899324370114428727718628785880647777
d = "1c7dfaeaeefcc88dc4a77870301126e11??????????????????????????????????"

# pisahkan known dan unkown dulu
_prefix = d.split("?")[0]
_prefix_hex = _prefix
_prefix_int = int(_prefix,16)

unkown_b = d.count("?") * 4

result = main(N, e, _prefix_int, unkown_b)
if result is None:
        raise SystemExit("failed to recover d")

d, p, q, k, idx, r, s = result
message = pow(C,d,N)
flag = long_to_bytes(message)
print(flag)
