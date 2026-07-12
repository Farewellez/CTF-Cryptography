# Weak - Write-up

## Challenge

- Category: Crypto
- Name: `Weak`
- Points: `157`
- Author: `hilmo`

## Source Review

The relevant flow is:

```python
def register(name):
    token = pce(name)

    data = {
        "name": name,
        "user_id": random.randint(1, 100),
        "token": token,
    }

    cookie = jwt.encode(data, secret, algorithm="HS256")
```

and on login:

```python
decoded = jwt.decode(cookie, secret, algorithms=["HS256"])

if decoded["name"] != name:
    print("Whoops! This cookie is not for you.")
    return

if decoded["name"] == "admin":
    print(pce_decrypt(decoded["token"].split("+")))
    if (
        decoded["name"]
        == pce_decrypt(decoded["token"].split("+")).split(";")[0].split("=")[1]
        and rand.hex() == decoded["token"].split("+")[2]
    ):
        print("GG, here your flag: ", FLAG)
```

The service stores:

- `name`
- `user_id`
- `token`

inside an `HS256` JWT.

The encrypted `token` is:

```python
f"{ciphertext.hex()}+{iv.hex()}+{rand.hex()}"
```

The intended admin check is:

1. JWT must be valid.
2. JWT field `name` must be `admin`.
3. Decrypted AES-CBC plaintext must begin with `name=admin`.
4. The trailing `rand` inside the token must match the global `rand`.

## Vulnerability

There are two weaknesses:

### 1. Weak JWT secret

The description already hints at it:

> "I think using a common secret is a bad idea"

So the first step is to register a normal account, get a JWT, and crack the HS256 secret offline using a common-secret wordlist.

The secret is:

```text
internet
```

Once we know that, we can forge arbitrary JWT payloads.

### 2. AES-CBC IV malleability

Even without the AES key, CBC lets us modify the first plaintext block by changing the IV:

```text
P1 = D(C1) xor IV
```

If we know the original first block and want a chosen first block, we can compute:

```text
IV' = IV xor P1_original xor P1_target
```

That changes only the first plaintext block after decryption.

## Why this works

The plaintext format is:

```text
name=<input>_<prefix...>;uid=<random>
```

We choose a username of length `10`, for example:

```text
AAAAAAAAAA
```

Then the first 16-byte block becomes exactly:

```text
name=AAAAAAAAAA_
```

Count it:

- `name=` = 5 bytes
- `AAAAAAAAAA` = 10 bytes
- `_` = 1 byte

Total = 16 bytes.

That makes the entire first block known.

We want the decrypted first block to become:

```text
name=admin;uid=1
```

This is also exactly 16 bytes.

So we keep the ciphertext unchanged and replace the IV with:

```text
IV' = IV xor b"name=AAAAAAAAAA_" xor b"name=admin;uid=1"
```

After that, decryption starts with:

```text
name=admin;uid=1...
```

The remainder of the plaintext is garbage-like but still valid enough because the program only checks:

- the first field is `name=admin`
- the appended `rand` still matches

The `rand` part is not encrypted, so we just preserve it.

## Exploitation Steps

1. Register any non-admin user and collect the JWT.
2. Crack the JWT signing secret offline.
3. Register a second user with a 10-byte name such as `AAAAAAAAAA`.
4. Extract `ciphertext`, `iv`, and `rand` from the token field.
5. Compute a forged IV so the first decrypted block becomes `name=admin;uid=1`.
6. Change the JWT `name` claim to `admin`.
7. Re-sign the JWT with the recovered secret `internet`.
8. Login as `admin` using the forged JWT.

## Exploit Script

```python
#!/usr/bin/env python3
import base64
import hashlib
import hmac
import json
import socket
import re

HOST = "challctf.find-it.id"
PORT = 7301
JWT_SECRET = b"internet"


def recvuntil(sock, marker):
    data = b""
    while marker not in data:
        chunk = sock.recv(4096)
        if not chunk:
            break
        data += chunk
    return data


def b64u(data):
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def jwt_sign(payload, secret):
    header = {"alg": "HS256", "typ": "JWT"}
    h = b64u(json.dumps(header, separators=(",", ":")).encode())
    p = b64u(json.dumps(payload, separators=(",", ":")).encode())
    msg = f"{h}.{p}".encode()
    sig = b64u(hmac.new(secret, msg, hashlib.sha256).digest())
    return f"{h}.{p}.{sig}"


def jwt_decode_noverify(token):
    header_b64, payload_b64, sig = token.split(".")
    payload = json.loads(
        base64.urlsafe_b64decode(payload_b64 + "=" * (-len(payload_b64) % 4))
    )
    return payload


def register(sock, name):
    recvuntil(sock, b"Enter your choice (1/2/3): ")
    sock.sendall(b"1\n")
    recvuntil(sock, b"Enter your name: ")
    sock.sendall(name.encode() + b"\n")
    out = recvuntil(sock, b"Enter your choice (1/2/3): ")
    m = re.search(rb"Store this cookie for login: ([A-Za-z0-9_\-\.]+)", out)
    if not m:
        raise RuntimeError("failed to parse cookie")
    return m.group(1).decode()


def login(sock, name, cookie):
    sock.sendall(b"2\n")
    recvuntil(sock, b"Enter your name: ")
    sock.sendall(name.encode() + b"\n")
    recvuntil(sock, b"Enter your cookie: ")
    sock.sendall(cookie.encode() + b"\n")
    return recvuntil(sock, b"Enter your choice (1/2/3): ").decode(errors="replace")


with socket.create_connection((HOST, PORT)) as sock:
    recvuntil(sock, b"Enter your choice (1/2/3): ")

    cookie = register(sock, "AAAAAAAAAA")
    payload = jwt_decode_noverify(cookie)

    enc_hex, iv_hex, rand_hex = payload["token"].split("+")
    iv = bytes.fromhex(iv_hex)

    original = b"name=AAAAAAAAAA_"
    target = b"name=admin;uid=1"
    forged_iv = bytes(a ^ b ^ c for a, b, c in zip(iv, original, target))

    payload["name"] = "admin"
    payload["token"] = f"{enc_hex}+{forged_iv.hex()}+{rand_hex}"
    forged_cookie = jwt_sign(payload, JWT_SECRET)

    result = login(sock, "admin", forged_cookie)
    print(result)
```

## Result

The forged login returns:

```text
GG, here your flag:  FindITCTF{W1_w0k_d3_t0k_n0t_0nl1_t0k_d3_t0k}
```

## Flag

```text
FindITCTF{W1_w0k_d3_t0k_n0t_0nl1_t0k_d3_t0k}
```
