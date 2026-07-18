# Byte-at-a-time ECB decryption (Simple)
Copy your oracle function to a new function that encrypts buffers under ECB mode using a consistent but unknown key (for instance, assign a single random key, once, to a global variable).

Now take that same function and have it append to the plaintext, BEFORE ENCRYPTING, the following string:
```
Um9sbGluJyBpbiBteSA1LjAKV2l0aCBteSByYWctdG9wIGRvd24gc28gbXkg
aGFpciBjYW4gYmxvdwpUaGUgZ2lybGllcyBvbiBzdGFuZGJ5IHdhdmluZyBq
dXN0IHRvIHNheSBoaQpEaWQgeW91IHN0b3A/IE5vLCBJIGp1c3QgZHJvdmUg
YnkK
```

### Spoiler alert.
Do not decode this string now. Don't do it.

Base64 decode the string before appending it. Do not base64 decode the string by hand; make your code do it. The point is that you don't know its contents.

What you have now is a function that produces:
```
AES-128-ECB(your-string || unknown-string, random-key)
```

It turns out: you can decrypt "unknown-string" with repeated calls to the oracle function!

Here's roughly how:

1. Feed identical bytes of your-string to the function 1 at a time --- start with 1 byte ("A"), then "AA", then "AAA" and so on. Discover the block size of the cipher. You know it, but do this step anyway.
2. Detect that the function is using ECB. You already know, but do this step anyways.
3. Knowing the block size, craft an input block that is exactly 1 byte short (for instance, if the block size is 8 bytes, make "AAAAAAA"). Think about what the oracle function is going to put in that last byte position.
4. Make a dictionary of every possible last byte by feeding different strings to the oracle; for instance, "AAAAAAAA", "AAAAAAAB", "AAAAAAAC", remembering the first block of each invocation.
5. Match the output of the one-byte-short input to one of the entries in your dictionary. You've now discovered the first byte of unknown-string.
6. Repeat for the next byte.

### Congratulations.
This is the first challenge we've given you whose solution will break real crypto. Lots of people know that when you encrypt something in ECB mode, you can see penguins through it. Not so many of them can decrypt the contents of those ciphertexts, and now you can. If our experience is any guideline, this attack will get you code execution in security tests about once a year.

## Write-Up
Challenge ini lumayan asik sebenarnya. Jadi di sini kita diminta untuk menebak sebuah secret _suffix_ yang ditambahkan setelah plaintext kita masuk ke _encryption oracle_. Di awal, kita diminta untuk menebak _block size_ encryption pada oracle ini karena oracle ini termasuk ke _block cipher_ (https://www.geeksforgeeks.org/ethical-hacking/block-cipher-modes-of-operation/). Setelah dapat sizenya, kita lanjut ke detect algoritma apa yang dipakai, karena kita baru tau CBC atau ECB kita coba detect 2 algoritma tersebut. Anggaplah kita dapat algoritma yang dipakai adalah ECB setelah mengirim payload dengan size _block size x 2_.

Next, kita bisa membuat function khusus untuk _breaking the oracle_ kita namai saja contoh ```break_oracle```. Tujuan function ini adalah mengirim payloads terus menerus ke program oracle dengan tujuan mengoleksi _dictonary key_ untuk tiap byte character ukuran ```block size - 1```. Contoh, kita dapat dari perhitungan sebelumnya block sizenya adalah 16, maka index ke 16-1 atau index ke-15 akan diisi oleh iterasi byte dari 0-255 sebagai value. Jadi ciphertext output sebagai key, dan 1 byte char sebagai value. Iterasi ini akan menggunakan while loop dan akan terus looping hingga ada block ciphertext yang tidak ditemukan di kamus dengan asumsi secret suffix plaintext sudah ditemukan.
