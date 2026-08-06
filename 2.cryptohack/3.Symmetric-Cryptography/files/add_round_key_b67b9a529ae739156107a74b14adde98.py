state = [
    [206, 243, 61, 34],
    [171, 11, 93, 31],
    [16, 200, 91, 108],
    [150, 3, 194, 51],
]

round_key = [
    [173, 129, 68, 82],
    [223, 100, 38, 109],
    [32, 189, 53, 8],
    [253, 48, 187, 78],
]


def add_round_key(s, k):
    M = [[] for _ in range(len(s))]
    for i in range(len(M)):
        M[i] = [s[i][j] ^ k[i][j] for j in range(len(M))]
    return M

print(add_round_key(state, round_key))

