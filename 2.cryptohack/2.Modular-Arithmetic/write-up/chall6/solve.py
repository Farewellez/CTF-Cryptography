from math import gcd
from sympy import sqrt_mod

def qs(p):
    uniq = set()
    for a in range(1,p):
        if gcd(a,p) != 1:
            continue
        uniq.add(pow(a,2,p))
    return uniq

ints=[14,6,11]
p = 29
quad_res = qs(p)
# print(quad_res)
for num in ints:
    if num not in quad_res:
        continue
    print(f"{num} is Quadratic Residue")
    root = [a for a in range(1,p) if pow(a,2,p) == num]
    print(f"root: {min(root)}")

# print(sqrt_mod(6, p))
    