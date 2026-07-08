from pwn import *

def get_ticket(username: bytes):
    io.recvuntil(b"> ")
    io.sendline(b"1")
    
    io.recvuntil(b"Username: ")
    io.sendline(username)
    
    io.recvuntil(b"Encrypted ticket:\n")
    ct = io.recvline().strip().decode()
    return ct

def usr_spoof(emperor: bytes):
    io.recvuntil(b"> ")
    io.sendline(b"2")

    io.recvuntil(b"Transmission: ")
    io.sendline(emperor)

    io.recvuntil(b"Ciphertext:\n")
    ct = io.recvline().strip().decode()
    return ct

def forged_ticket(ticket: bytes, emperor: bytes):
    payload = ticket + emperor
    
    io.recvuntil(b"> ")
    io.sendline(b"3")

    io.recvuntil(b"Encrypted ticket: ")
    io.sendline(payload.hex().encode())
    io.recvuntil(b"Access granted.\n")
    io.recvline()
    output = io.recvline()
    return output.strip().decode()

def find_flag(text: str):
    match = re.search(r"ACE\{.*?\}", text)
    return match.group(0) if match else None

HOST = "34.47.176.25"
PORT = 4901
# context.log_level = 'debug'
context.log_level = 'error'

io = remote(HOST, PORT)
username = b"AAAAA"
payload = b"emperor"

clean_ticket = get_ticket(username)
print(f"size length: {len(clean_ticket)//2}")
print(clean_ticket)

spoof_ticket = clean_ticket[:16*4]
print(f"size length: {len(spoof_ticket)//2}")
print(spoof_ticket)


emperor = usr_spoof(payload)
print(f"\nsize length: {len(emperor)//2}")
print(emperor)

result = forged_ticket(bytes.fromhex(spoof_ticket),bytes.fromhex(emperor))
flag = find_flag(result)
print(f"Flag: {flag}")
io.close()
