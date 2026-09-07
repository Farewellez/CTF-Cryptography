a = "sajcmijansjindjaiwdnaifbnaiowhebraiwhbeaouibcaicndoahcibawyibeiajsnvhriv hskbjdnfiuasnjfasundasidnasd"
words = {}
for w in a:
    if w not in words:
        words[w] = 1
        continue
    else:
        words[w] += 1
        continue

print(words)