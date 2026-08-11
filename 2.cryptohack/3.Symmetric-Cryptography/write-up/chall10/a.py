import requests

"""
Solves in only 41 HTTP requests, with 0 assumptions about flag format etc.
I achieve this by stuffing multiple trial plaintexts into each HTTP request,
and exiting early as soon as a matching block is found.
This code is over-optimised, sacrificing readability and thus educational value.
$ time python3 solve.py
...
solved in 41 HTTP requests!
real	0m0.587s
user	0m0.203s
sys	0m0.022s
FUTURE OPTIMISATIONS:
This script solves the plaintext left-to-right. It is also possible to solve
right-to-left. We could do both in parallel and "meet in the middle", to ~halve
the execution time.
https://gist.github.com/DavidBuchanan314/beb4b4998f4131806ba466cbdff9a83e
"""

s = requests.session()
rcount = 0
def encrypt(data):
	global rcount
	rcount += 1 # track HTTP request count, just for fun
	r = s.get(f"http://aes.cryptohack.org/ecb_oracle/encrypt/{data.hex()}/")
	return(bytes.fromhex(r.json()["ciphertext"]))


# split data across multiple requests, to deal with URL length restrictions
# returns a generator so the caller can early-exit
def encrypt_big(data):
	MAX_SIZE = 0x10*56
	for i in range((len(data)-1)//MAX_SIZE+1):
		block = data[i*MAX_SIZE:(i+1)*MAX_SIZE]
		ct = encrypt(block)[:len(block)]
		for j in range(len(ct)//0x10):
			yield ct[j*0x10:(j+1)*0x10]


# put most common byte values first, so we can early-exit sooner on average
charset = list(b"etoanihsrdlucgwyfmpbkvjxqz{}_01234567890ETOANIHSRDLUCGWYFMPBKVJXQZ")
for i in range(0x100): # include all the other byte values in the charset too
	if i not in charset:
		charset.append(i)

# cache ciphertexts at all 16 possible offsets
targets = [encrypt(b"A"*(0x10-i)) for i in range(0x10)]

# we can work out the length of the flag based on when the padded length "steps up"
lengths = list(map(len, targets))
flag_len = lengths[-1] - 0x11 + lengths.index(lengths[-1])

flag = b""
for _ in range(flag_len):
	# XXX: there are multiple off-by-one bugs here, that all cancel out. Trust me.
	b, i = divmod(len(flag) + 1, 0x10)
	target = targets[i][b*0x10:(b+1)*0x10] # get the ciphertext of that block

	attempts = b""
	for c in charset:
		attempts += (b"A"*0x10+flag+bytes([c]))[-0x10:]

	for c, ct in zip(charset, encrypt_big(attempts)):
		if ct == target:
			flag += bytes([c])
			print(flag)
			break
	else:
		exit("oof")

print(f"solved in {rcount} HTTP requests!")
