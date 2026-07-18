# Implement PKCS#7 padding
def pkcs7(plaintext: str, block_size = 16): return plaintext.encode() + (bytes([abs(block_size - len(plaintext))]) * abs(block_size - len(plaintext))) 
print(pkcs7("YELLOW SUBMARINE", 20))
