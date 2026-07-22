# Favourite byte
For the next few challenges, you'll use what you've just learned to solve some more XOR puzzles.

I've hidden some data using XOR with a single byte, but that byte is a secret. Don't forget to decode from hex first.

```
73626960647f6b206821204f21254f7d694f7624662065622127234f726927756d
```

## Write-Up
Di sini kita dapat sebuah ciphertext yang perlu kita decrypt, namun masalahnya kita tidak tahu key yang dipakai untuk single-byte XOR di sini. Jadi kita perlu melakukan bruteforcing terhadap byte-per-byte dari ciphertext dengan ```for loop``` yang didalamnya melakukan XOR operate terdahap i, 0 <= i <= 255 | i ∈ ℤ. Jika dalam hasil decrypt terdapat kaya "crypto" kita bisa break loopingnya.

```
(venv_linux) kurumi@LAPTOP-B49Q3K5D:/mnt/d/my-kisah/crypto/2.cryptohack/1.Introduction-to-CryptoHack/write-up/chall_9$ python3 solve.py 
crypto{0x10_15_my_f4v0ur173_by7e}
```
