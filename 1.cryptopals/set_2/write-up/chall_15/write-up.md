# PKCS#7 padding validation
Write a function that takes a plaintext, determines if it has valid PKCS#7 padding, and strips the padding off.

The string:
```
"ICE ICE BABY\x04\x04\x04\x04"
```
... has valid padding, and produces the result "ICE ICE BABY".

The string:
```
"ICE ICE BABY\x05\x05\x05\x05"
```
... does not have valid padding, nor does:
```
"ICE ICE BABY\x01\x02\x03\x04"
```
If you are writing in a language with exceptions, like Python or Ruby, make your function throw an exception on bad padding.

Crypto nerds know where we're going with this. Bear with us.

## Write-Up
Jadi di sini kita diminta untuk melakukan validasi terhadap sebuah padded pkcs#7 string. Rumus yang bisa kita dapat yaitu dengan menghitung:
1. block size: Ini bisa kita dapat dengan menghitung length dari ciphertext
2. difference padding yang dipakai dengan mengambil byte terakhir dari ciphertext

Setelah dapat dua itu, kita perlu cek apakah padding length atau difference di point 2 itu = 0 atau melebihi block size, jika iya bisa dipastikan padding pkcs#7 nya invalid. Kondisi lain yaitu jika kita ambil ```ciphertext[-padd_len:]``` ternyata tidak sama dengan ```bytes([padd_len]*padd_len)``` maka bisa dipastikan kalau paddingnya invalid. Jika tidak memnuhi 2 kondisi tersebut, maka bisa dipastikan kalau paddingnya valid.
