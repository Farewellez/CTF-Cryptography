# Implement PKCS#7 padding
A block cipher transforms a fixed-sized block (usually 8 or 16 bytes) of plaintext into ciphertext. But we almost never want to transform a single block; we encrypt irregularly-sized messages.

One way we account for irregularly-sized messages is by padding, creating a plaintext that is an even multiple of the blocksize. The most popular padding scheme is called PKCS#7.

So: pad any block to a specific block length, by appending the number of bytes of padding to the end of the block. For instance,
```
"YELLOW SUBMARINE"
```

... padded to 20 bytes would be:
```
"YELLOW SUBMARINE\x04\x04\x04\x04"
```

## Write-Up
Jadi kita diajarkan soal PKCS#7 di sini (https://en.wikipedia.org/wiki/PKCS_7). Salah satu skema padding yang bisa bekerja sebagai mekanisme padding berdasarkan ukuran block. PKCS#7 dapat menampung block apapun dalam rentang ukuran 1 - 255 bytes (https://crypto.stackexchange.com/questions/9043/what-is-the-difference-between-pkcs5-padding-and-pkcs7-padding). Di sini caranya kita perlu menggunakan rumus:
```
plaintext += "{len(block) - len(plaintext)}"*len(block) - len(plaintext)
```
Cukup mudah untuk mengimplementasikannya di kode python.
