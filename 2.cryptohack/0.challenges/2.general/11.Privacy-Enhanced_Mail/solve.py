# https://www.thesecuritybuddy.com/cryptography-and-python/how-to-export-and-import-rsa-keys-using-the-pycryptodome-module-in-python/2/
from Crypto.PublicKey import RSA

with open("privacy_enhanced_mail_1f696c053d76a78c2c531bb013a92d4a.pem","rb") as f:
    priv_key = RSA.importKey(f.read(),'MyPassphrase')

print(priv_key.d)