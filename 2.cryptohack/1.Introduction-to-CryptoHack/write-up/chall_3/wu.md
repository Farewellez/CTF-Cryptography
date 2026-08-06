## ASCII
ASCII is a 7-bit encoding standard which allows the representation of text using the integers 0-127.

Using the below integer array, convert the numbers to their corresponding ASCII characters to obtain a flag.
```
[99, 114, 121, 112, 116, 111, 123, 65, 83, 67, 73, 73, 95, 112, 114, 49, 110, 116, 52, 98, 108, 51, 125]
```

> In Python, the chr() function can be used to convert an ASCII ordinal number to a character (the ord() function does the opposite).


## Write-Up
Di sini, kita diajarkan soal ascii oleh cryptohack. ASCII sendiri juga dapat berbentuk sebuah angka ordinal dengan method ```ord()``` di python dan dapat berupa printable character dengan method ```chr()``` di python. Kita diminta convert ascii ordinal number ke bentuk character menggunakan ```chr()```. Cukup buat kode for loop simple tiap element list lalu convert ke char.

```
kurumi@LAPTOP-B49Q3K5D:/mnt/d/my-kisah/crypto/2.cryptohack/1.Introduction-to-CryptoHack/write-up/chall_3$ python3 solve.py 
crypto{ASCII_pr1nt4bl3}
```