import math
import re
from pathlib import Path

from fpylll import IntegerMatrix, LLL
from sympy import Poly, ZZ, symbols

def polynomial_multiply(a, b):
    result = [0] * (len(a) + len(b) - 1)

    for i, coefficient_a in enumerate(a):
        for j, coefficient_b in enumerate(b):
            result[i + j] += coefficient_a * coefficient_b

    return result

def polynomial_power(polynomial, exponent):
    result = [1]

    for _ in range(exponent):
        result = polynomial_multiply(result, polynomial)

    return result

def coppersmith_linear_factor(N, pref_bit, unk_bit, suff_bit):
    prefix_length = len(prefix_bits)
    unknown_length = len(unknown_bits)
    suffix_length = len(suffix_bits)

    prefix = int(prefix_bits, 2)
    suffix = int(suffix_bits, 2)

    # kita pake beberapa formula dan pendektan shift like before
    # p = A*x + B
    # A = 2^suffix_length
    # B = prefix * 2^(unknown_length + suffix_length) + suffix
    A = 1 << suffix_length
    B = (prefix << (unknown_length + suffix_length)) | suffix


    # now we got this:
    # A*x + B == 0 mod p
    # Supaya polinomial menjadi monic, kita coba kalikan dengan A^-1:
    # x + B*A^-1 == 0 mod p
    inverse_A = pow(A, -1, N)
    constant = (B * inverse_A) % N

    # f(x) = x + constant
    # Format koefisien:
    # [constant, 1]
    f = [constant, 1]

    # Batas akar:
    # 0 <= x < 2^unknown_length
    X = 1 << unknown_length

    # Parameter lattice.
    # Dimensi lattice = m + t = 6.
    m = 3
    t = 3

    lattice_polynomials = []
    for i in range(m):
        polynomial = polynomial_power(f, i)
        multiplier = N ** (m - i)

        polynomial = [
            coefficient * multiplier
            for coefficient in polynomial
        ]

        lattice_polynomials.append(polynomial)

    f_power_m = polynomial_power(f, m)

    for j in range(t):
        polynomial = ([0] * j) + f_power_m
        lattice_polynomials.append(polynomial)

    dimension = len(lattice_polynomials)

    # now we got the lattice dan kita sekarang build matrixnya lalu lanjut dengan LLL reduction
    lattice = IntegerMatrix(dimension, dimension)
    for row_index, polynomial in enumerate(lattice_polynomials):
        for degree in range(dimension):
            if degree < len(polynomial):
                coefficient = polynomial[degree]
            else:
                coefficient = 0

            lattice[row_index, degree] = (coefficient * (X ** degree))

    LLL.reduction(lattice, delta=0.99)
    x_symbol = symbols("x")
    for row_index in range(dimension):
        coefficients = []
        valid_row = True

        for degree in range(dimension):
            value = int(lattice[row_index, degree])
            scale = X ** degree

            if value % scale != 0:
                valid_row = False
                break

            coefficients.append(value // scale)

        if not valid_row:
            continue

        expression = sum(coefficients[degree] * x_symbol**degree for degree in range(len(coefficients)))
        polynomial = Poly(expression,x_symbol,domain=ZZ,).primitive()[1]


        roots = polynomial.ground_roots()

        for root in roots:
            root = int(root)

            if not 0 <= root < X:
                continue

            candidate_p = A * root + B
            factor = math.gcd(candidate_p, N)

            if factor in (1, N):
                continue

            if N % factor != 0:
                continue

            p = factor
            q = N // p

            print(f"Root ada di lattice row {row_index}")
            print(f"Unknown middle: {root}")
            print(f"Unknown bits  : {root.bit_length()} bit")

            return p, q

def decrypt_rsa(N,e,ciphertext,p,q):
    phi = (p - 1) * (q - 1)
    d = pow(e, -1, phi)

    plaintext_integer = pow(ciphertext, d, N)

    plaintext_length = max(1,(plaintext_integer.bit_length() + 7) // 8,)

    return plaintext_integer.to_bytes(plaintext_length,"big",)

N = 80329589900848116233988882207375979703121859486146305045816492666964968431294552070408716008243121191783239071478515627573994596834773273847417073356518568709416991168147566693847145648646025262320546610493721479789958890761574201773327276539921327394182396030193653421455891376888536611596300960119551975757
e = 65537
C = 10727007459887951081038288006334718838121029247037460588430504700466653165041190727066716664156880960559125796752321978327460646167339985445249541182663517597078602662671105431479469194649714951502904638070509652906007703481647501664723560678352827805551279409891077312786523091521032575731473451504693476715
_p = "100001100000011010011000010100100111100010011011101010011110101110010101000011011111100011000011110011010010110010010111011110011100101111101001101100????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????100011010100100010100001110010111000101010000101100011111001000011001010000101001100100010101101101100000010000010110010001101001000011110010111001011000010010001" 

bit_groups = re.fullmatch(r"([01]+)(\?+)([01]+)",_p,)
prefix_bits, unknown_bits, suffix_bits = bit_groups.groups()

p, q = coppersmith_linear_factor(N,prefix_bits,unknown_bits,suffix_bits,)
print(f"p: {p}")
print(f"q: {q}")
print(f"p.q = N -> {p*q == N}")

pt = decrypt_rsa(N, e, C, p, q)
print(pt)
