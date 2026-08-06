# reference: https://www.youtube.com/watch?v=e8DtzQkjOMQ&t=692s
def chinese_remainder_theorem(ai, mi):
    M = []
    M_inv = []
    for i in range(len(mi)):
        Mi = 1
        for j in range(len(mi)):
            if i == j:
                continue
            Mi *= mi[j]
        M.append(Mi)

    for i in range(len(M)):
        M_inv.append(pow(M[i], -1, mi[i]))

    bigM = 1
    for x in mi:
        bigM *= x

    X = 0
    for i in range(len(ai)):
        X += (ai[i]*M[i]*M_inv[i])

    return X % bigM

ai = [2,3,5] 
mi = [5,11,17]
M = 935
x = chinese_remainder_theorem(ai,mi)
a = x % M
print(a)