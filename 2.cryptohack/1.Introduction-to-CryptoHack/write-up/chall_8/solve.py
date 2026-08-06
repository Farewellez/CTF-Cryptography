# XOR Properties
def fixed_xor(b1: bytes, b2: bytes):
    if len(b1) - len(b2) != 0:
        raise Exception("buffer must have same length")
    return bytes(bytearray([x ^ y for x, y in zip(b1, b2)]))

flag = fixed_xor(fixed_xor(bytes.fromhex("04ee9855208a2cd59091d04767ae47963170d1660df7f56f5faf"), bytes.fromhex("a6c8b6733c9b22de7bc0253266a3867df55acde8635e19c73313")), bytes.fromhex("c1545756687e7573db23aa1c3452a098b71a7fbf0fddddde5fc1"))
print(flag.decode())