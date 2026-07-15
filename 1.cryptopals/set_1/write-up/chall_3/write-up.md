# Single-byte XOR cipher
The hex encoded string:
```
1b37373331363f78151b7f2b783431333d78397828372d363c78373e783a393b3736
```

... has been XOR'd against a single character. Find the key, decrypt the message.

You can do this by hand. But don't: write code to do it for you.

How? Devise some method for "scoring" a piece of English plaintext. Character frequency is a good metric. Evaluate each output and choose the one with the best score.

### Achievement Unlocked
You now have our permission to make "ETAOIN SHRDLU" jokes on Twitter.

## Write-Up
Jadi di sini kita diberikan sebuah hex string yang jika kita coba decode maka hasil keluarannya akan acak. Karena nama challenge nya adalah "Single-byte XOR cipher", jadi kita perlu melakukan bruteforcing pada 256 byte terhadap seluruh character ciphertext lalu melakukan scoring. Scoring di sini bertujuan agar kita bisa melakukan analisis statis berdasarkan huruf yang sering keluar dalam sebuah kalimat bahasa inggris atau Letter frequency (https://en.wikipedia.org/wiki/Letter_frequency) dengan top character saat ini yaitu "ETAOIN SHRDLU".

Karena hasilnya bisa saja meleset, atau tidak pasti ada di peringkat pertama scoring, jadi kita bisa ambil contoh di sini 5 kandidat plaintext yang kita inginkan.
