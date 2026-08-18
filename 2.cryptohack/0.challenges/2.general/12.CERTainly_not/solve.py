# https://stackoverflow.com/questions/18806962/simple-der-cert-parsing-in-python
from asn1crypto.x509 import Certificate

with open("2048b-rsa-example-cert_3220bd92e30015fe4fbeb84a755e7ca5.der", "rb") as f:
    cert = Certificate.load(f.read())

n = cert.public_key.native["public_key"]["modulus"]
print(n)