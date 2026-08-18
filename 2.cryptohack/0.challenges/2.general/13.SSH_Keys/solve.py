# https://www.pythontutorials.net/blog/how-do-you-extract-n-and-e-from-a-rsa-public-key-in-python/#option-2-load-openssh-directly-with-cryptography
from cryptography.hazmat.primitives import serialization

with open("bruce_rsa_6e7ecd53b443a97013397b1a1ea30e14.pub", "rb") as f:
    public_key = serialization.load_ssh_public_key(  
        f.read()  
    )

pubkey = public_key.public_numbers()
n = pubkey.n
print(n)