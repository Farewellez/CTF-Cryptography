#!/usr/bin/env python3
from pwn import remote, context
from Crypto.Util.number import bytes_to_long
import re

context.log_level = "info"

HOST = "34.47.176.25"
PORT = 4904

TARGET = bytes_to_long(b"ImperialAdministrator")


def sign_oracle(r, role_int):
    r.recvuntil(b"> ")
    r.sendline(b"1")

    r.recvuntil(b"role > ")
    r.sendline(str(role_int).encode())

    data = r.recvuntil(b"> ")

    m = re.search(rb"Authorization Signature:\s*\n([0-9]+)", data)
    if not m:
        raise RuntimeError("Failed to parse signature")

    return int(m.group(1))


def gate_submit(r, signature_int):
    r.sendline(b"3")

    r.recvuntil(b"signature > ")
    r.sendline(str(signature_int).encode())

    data = r.recvuntil(b"> ", timeout=5)
    return data


def main():
    r = remote(HOST, PORT)

    # TARGET is even:
    # bytes_to_long(b"ImperialAdministrator")
    # = 2 * (TARGET // 2)
    a = 2
    b = TARGET // 2

    assert a * b == TARGET

    sig_a = sign_oracle(r, a)
    sig_b = sign_oracle(r, b)

    # Textbook RSA signature is multiplicative:
    # sig(a) * sig(b) = a^d * b^d = (a*b)^d mod N
    forged_sig = sig_a * sig_b

    result = gate_submit(r, forged_sig)
    print(result.decode(errors="replace"))

    r.close()


if __name__ == "__main__":
    main()