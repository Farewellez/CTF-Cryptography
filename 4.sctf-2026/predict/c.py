#!/usr/bin/env python3
import argparse
import sys
from dataclasses import dataclass
from typing import Dict, List, Tuple


# =========================
# MT19937 constants
# =========================

N = 624
M = 397
WORD_BITS = 32
NUM_STATE_BITS = N * WORD_BITS

MATRIX_A = 0x9908B0DF
UPPER_MASK = 0x80000000
LOWER_MASK = 0x7FFFFFFF

DEFAULT_CIPHERTEXT_HEX = (
    "38c9e92b118434a05e9bffd360560206"
    "1268d420ab9bda37849b6fc99ff85c81"
    "564a6a4476b6144ccea81714e243eca0"
    "b32db8cdc0a40afb37cb810c48a16e80"
)


# =========================
# Utility
# =========================

def load_leaks(path: str) -> List[int]:
    leaks: List[int] = []

    with open(path, "r", encoding="utf-8") as f:
        for lineno, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue

            try:
                value = int(line, 10)
            except ValueError:
                raise ValueError(f"line {lineno}: not an integer: {line!r}")

            if not (0 <= value <= 255):
                raise ValueError(f"line {lineno}: value outside 0..255: {value}")

            leaks.append(value)

    if len(leaks) != 2500:
        raise ValueError(f"expected exactly 2500 leaks, got {len(leaks)}")

    return leaks


def parse_hex_bytes(hex_string: str) -> bytes:
    try:
        data = bytes.fromhex(hex_string)
    except ValueError as e:
        raise ValueError(f"invalid ciphertext hex: {e}") from e

    if len(data) == 0 or len(data) % 16 != 0:
        raise ValueError("ciphertext length must be non-zero and multiple of 16 bytes")

    return data


def int128_to_le_bytes(value: int) -> List[int]:
    return [(value >> (8 * i)) & 0xFF for i in range(16)]


def format_c_array_u8(name: str, data: List[int], indent: str = "") -> str:
    body = ", ".join(f"0x{x:02x}" for x in data)
    return f"{indent}static const uint8_t {name}[16] = {{ {body} }};\n"


def format_2d_c_array_u8(name: str, rows: List[List[int]], indent: str = "") -> str:
    out = []
    out.append(f"{indent}static const uint8_t {name}[FUTURE_RANK][16] = {{\n")
    for row in rows:
        body = ", ".join(f"0x{x:02x}" for x in row)
        out.append(f"{indent}    {{ {body} }},\n")
    out.append(f"{indent}}};\n")
    return "".join(out)


def format_bytes_array(name: str, data: bytes, indent: str = "") -> str:
    out = []
    out.append(f"{indent}static const uint8_t {name}[CIPHERTEXT_LEN] = {{\n")

    for i in range(0, len(data), 16):
        chunk = data[i:i + 16]
        body = ", ".join(f"0x{x:02x}" for x in chunk)
        out.append(f"{indent}    {body},\n")

    out.append(f"{indent}}};\n")
    return "".join(out)


# =========================
# Symbolic 32-bit word
# =========================
#
# Word representation:
#   word[bit_index] = Python int bitset over initial MT state bits.
#
# Bit order:
#   LSB-first, so word[0] is bit 0.
# =========================

Word = List[int]


def word_zero() -> Word:
    return [0] * WORD_BITS


def word_copy(w: Word) -> Word:
    return w[:]


def word_xor(a: Word, b: Word) -> Word:
    return [x ^ y for x, y in zip(a, b)]


def word_shift_right(w: Word, shift: int) -> Word:
    out = [0] * WORD_BITS
    for i in range(WORD_BITS - shift):
        out[i] = w[i + shift]
    return out


def word_shift_left(w: Word, shift: int) -> Word:
    out = [0] * WORD_BITS
    for i in range(shift, WORD_BITS):
        out[i] = w[i - shift]
    return out


def word_and_const(w: Word, mask: int) -> Word:
    out = [0] * WORD_BITS
    for i in range(WORD_BITS):
        if (mask >> i) & 1:
            out[i] = w[i]
    return out


def temper_word(y: Word) -> Word:
    y = word_xor(y, word_shift_right(y, 11))
    y = word_xor(y, word_and_const(word_shift_left(y, 7), 0x9D2C5680))
    y = word_xor(y, word_and_const(word_shift_left(y, 15), 0xEFC60000))
    y = word_xor(y, word_shift_right(y, 18))
    return y


# =========================
# Symbolic MT19937
# =========================

class SymbolicMT19937:
    def __init__(self, start_index: int = 0):
        if not (0 <= start_index <= N):
            raise ValueError("start_index must be in 0..624")

        self.mt: List[Word] = []
        for word_idx in range(N):
            w = []
            for bit_idx in range(WORD_BITS):
                state_bit_index = word_idx * WORD_BITS + bit_idx
                w.append(1 << state_bit_index)
            self.mt.append(w)

        self.index = start_index

    def twist(self) -> None:
        # Standard MT19937 in-place twist.
        # This intentionally uses already-updated mt elements when the reference
        # implementation does so.
        for i in range(N):
            j = (i + 1) % N
            k = (i + M) % N

            # y = (mt[i] & UPPER_MASK) | (mt[j] & LOWER_MASK)
            y = [0] * WORD_BITS

            # LOWER_MASK keeps bits 0..30 from mt[j].
            for b in range(31):
                y[b] = self.mt[j][b]

            # UPPER_MASK keeps bit 31 from mt[i].
            y[31] = self.mt[i][31]

            y_lsb = y[0]

            new_word = [0] * WORD_BITS
            for b in range(WORD_BITS):
                v = self.mt[k][b]

                # y >> 1
                if b + 1 < WORD_BITS:
                    v ^= y[b + 1]

                # if y is odd, xor MATRIX_A.
                # Symbolically: xor y_lsb into every bit where MATRIX_A has 1.
                if (MATRIX_A >> b) & 1:
                    v ^= y_lsb

                new_word[b] = v

            self.mt[i] = new_word

    def extract_number_symbolic(self) -> Word:
        if self.index >= N:
            self.twist()
            self.index = 0

        y = temper_word(self.mt[self.index])
        self.index += 1
        return y


# =========================
# GF(2) Gaussian elimination
# =========================
#
# Augmented row representation:
#   bits 0..NUM_STATE_BITS-1 : coefficients
#   bit NUM_STATE_BITS       : RHS
# =========================

class GF2Eliminator:
    def __init__(self, nvars: int):
        self.nvars = nvars
        self.rhs_bit = 1 << nvars
        self.coeff_mask = self.rhs_bit - 1
        self.pivots: Dict[int, int] = {}

    def add_row(self, coeff: int, rhs: int) -> None:
        if rhs not in (0, 1):
            raise ValueError("rhs must be 0 or 1")

        row = coeff | (rhs << self.nvars)

        while True:
            c = row & self.coeff_mask

            if c == 0:
                if (row >> self.nvars) & 1:
                    raise ValueError("inconsistent constraint system")
                return

            pivot = c.bit_length() - 1
            existing = self.pivots.get(pivot)

            if existing is None:
                self.pivots[pivot] = row
                return

            row ^= existing

    @property
    def rank(self) -> int:
        return len(self.pivots)

    @property
    def free_bits(self) -> int:
        return self.nvars - self.rank

    def reduce_linear_form(self, coeff: int) -> Tuple[int, int]:
        """
        Reduce a linear form L(x) over the affine solution space.

        Return:
            const_bit, free_expr

        Meaning:
            L(x) = const_bit XOR dot(free_expr, free_variables)
        """
        rem = coeff
        expr = 0
        const = 0

        while rem:
            pivot = rem.bit_length() - 1
            row = self.pivots.get(pivot)

            if row is not None:
                rem ^= row & self.coeff_mask
                const ^= (row >> self.nvars) & 1
            else:
                expr |= 1 << pivot
                rem ^= 1 << pivot

        return const, expr


# =========================
# Future key projection
# =========================

@dataclass
class RecoveryResult:
    start_index: int
    constraint_rank: int
    free_state_bits: int
    future_rank: int
    base_key_int: int
    delta_key_ints: List[int]
    ciphertext: bytes


def insert_basis_vector(v: int, basis: Dict[int, int]) -> bool:
    x = v

    while x:
        pivot = x.bit_length() - 1
        existing = basis.get(pivot)

        if existing is None:
            basis[pivot] = x
            return True

        x ^= existing

    return False


def recover_for_start_index(
    leaks: List[int],
    start_index: int,
    ciphertext: bytes,
) -> RecoveryResult:
    mt = SymbolicMT19937(start_index=start_index)
    elim = GF2Eliminator(NUM_STATE_BITS)

    for out_idx, leaked_byte in enumerate(leaks):
        symbolic_output = mt.extract_number_symbolic()

        # IMPORTANT:
        # Leak is LSB byte only, so constrain bits 0..7.
        # Do not use bits 24..31.
        for bit in range(8):
            rhs = (leaked_byte >> bit) & 1
            coeff = symbolic_output[bit]
            elim.add_row(coeff, rhs)

        if (out_idx + 1) % 500 == 0:
            print(
                f"[+] processed {out_idx + 1:4d}/2500 leaks, "
                f"rank={elim.rank}",
                flush=True,
            )

    # Generate the 4 full MT outputs immediately after the 2500 leaked outputs.
    future_words: List[Word] = []
    for _ in range(4):
        future_words.append(mt.extract_number_symbolic())

    # key = struct.pack("<IIII", out2500, out2501, out2502, out2503)
    base_key_int = 0
    key_bit_exprs: List[int] = []

    for word_idx, w in enumerate(future_words):
        for bit_idx in range(WORD_BITS):
            key_bit_index = word_idx * WORD_BITS + bit_idx
            const, expr = elim.reduce_linear_form(w[bit_idx])

            if const:
                base_key_int |= 1 << key_bit_index

            key_bit_exprs.append(expr)

    # Convert the free-variable representation into a 128-bit keyspace basis.
    #
    # For every free state variable f, compute its 128-bit effect on the AES key.
    free_var_to_key_delta: Dict[int, int] = {}

    for key_bit_index, expr in enumerate(key_bit_exprs):
        e = expr
        while e:
            lsb = e & -e
            free_var = lsb.bit_length() - 1
            free_var_to_key_delta[free_var] = (
                free_var_to_key_delta.get(free_var, 0) ^ (1 << key_bit_index)
            )
            e ^= lsb

    basis: Dict[int, int] = {}
    for delta in free_var_to_key_delta.values():
        if delta != 0:
            insert_basis_vector(delta, basis)

    # Deterministic order.
    delta_key_ints = [basis[p] for p in sorted(basis.keys(), reverse=True)]

    return RecoveryResult(
        start_index=start_index,
        constraint_rank=elim.rank,
        free_state_bits=elim.free_bits,
        future_rank=len(delta_key_ints),
        base_key_int=base_key_int,
        delta_key_ints=delta_key_ints,
        ciphertext=ciphertext,
    )


def write_generated_header(result: RecoveryResult, out_path: str) -> None:
    base_key = int128_to_le_bytes(result.base_key_int)
    delta_keys = [int128_to_le_bytes(x) for x in result.delta_key_ints]

    with open(out_path, "w", encoding="utf-8") as f:
        f.write("#ifndef GENERATED_KEYSPACE_H\n")
        f.write("#define GENERATED_KEYSPACE_H\n\n")
        f.write("#include <stdint.h>\n")
        f.write("#include <stddef.h>\n\n")

        f.write("/* Auto-generated by recover_mt.py */\n")
        f.write(f"/* start_index      : {result.start_index} */\n")
        f.write(f"/* constraint rank  : {result.constraint_rank} */\n")
        f.write(f"/* free state bits  : {result.free_state_bits} */\n")
        f.write(f"/* future rank      : {result.future_rank} */\n\n")

        f.write(f"#define FUTURE_RANK {result.future_rank}\n")
        f.write(f"#define CIPHERTEXT_LEN {len(result.ciphertext)}\n\n")

        f.write(format_c_array_u8("BASE_KEY", base_key))
        f.write("\n")
        f.write(format_2d_c_array_u8("DELTA_KEYS", delta_keys))
        f.write("\n")
        f.write(format_bytes_array("CIPHERTEXT", result.ciphertext))
        f.write("\n")

        f.write("#endif /* GENERATED_KEYSPACE_H */\n")


def print_result_log(result: RecoveryResult, out_path: str) -> None:
    print()
    print("[+] recovery complete")
    print(f"[+] start index      : {result.start_index}")
    print(f"[+] loaded leaks     : 2500")
    print(f"[+] constraint rank  : {result.constraint_rank}")
    print(f"[+] free state bits  : {result.free_state_bits}")
    print(f"[+] future rank      : {result.future_rank}")
    print(f"[+] candidate keys   : 2^{result.future_rank}")
    print(f"[+] header written   : {out_path}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Recover reduced AES keyspace from MT19937 LSB-byte leaks."
    )
    parser.add_argument("predictable_txt", help="file containing 2500 leaked integers")
    parser.add_argument(
        "--start-index",
        type=int,
        default=0,
        help="MT index at first leaked output, default: 0",
    )
    parser.add_argument(
        "--scan-start-index",
        action="store_true",
        help="try start indexes 0..623 and emit generated_keyspace.startXXX.h files",
    )
    parser.add_argument(
        "--ciphertext",
        default=DEFAULT_CIPHERTEXT_HEX,
        help="ciphertext hex",
    )
    parser.add_argument(
        "--out",
        default="generated_keyspace.h",
        help="output header path, default: generated_keyspace.h",
    )

    args = parser.parse_args()

    try:
        leaks = load_leaks(args.predictable_txt)
        ciphertext = parse_hex_bytes(args.ciphertext)

        print(f"[+] loaded leaks     : {len(leaks)}")
        print(f"[+] ciphertext bytes : {len(ciphertext)}")

        if args.scan_start_index:
            best = None

            for start_index in range(N):
                print()
                print(f"[+] scanning start-index={start_index}")
                result = recover_for_start_index(leaks, start_index, ciphertext)
                out_path = f"generated_keyspace.start{start_index:03d}.h"
                write_generated_header(result, out_path)
                print_result_log(result, out_path)

                if best is None or result.future_rank < best.future_rank:
                    best = result

            if best is not None:
                write_generated_header(best, args.out)
                print()
                print(
                    f"[+] best future rank was {best.future_rank} "
                    f"at start-index={best.start_index}"
                )
                print(f"[+] copied best candidate header to {args.out}")

        else:
            result = recover_for_start_index(leaks, args.start_index, ciphertext)
            write_generated_header(result, args.out)
            print_result_log(result, args.out)

        return 0

    except Exception as e:
        print(f"[-] error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
