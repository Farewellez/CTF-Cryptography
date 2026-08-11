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

def matrix2bytes(s):
    return bytes(sum(s,[]))

# def add_round_key(s, k):
#     for i in range(len(s)):    
#         for j in range(len(s[i])):
#             s[i][j] ^= k[i][j]
#     return matrix2bytes(s)

def add_round_key(s, k):
    return [[sss^kkk for sss, kkk in zip(ss, kk)] for ss, kk in zip(s, k)]

print(matrix2bytes(add_round_key(state, round_key)))
