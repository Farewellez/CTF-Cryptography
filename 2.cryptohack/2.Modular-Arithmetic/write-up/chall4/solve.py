from math import gcd
p = 65537
a = 273246787654

print(gcd(a,p))
print(pow(a,p-1,p))