# Bytes and Big Integers
Cryptosystems like RSA works on numbers, but messages are made up of characters. How should we convert our messages into numbers so that mathematical operations can be applied?

The most common way is to take the ordinal bytes of the message, convert them into hexadecimal, and concatenate. This can be interpreted as a base-16/hexadecimal number, and also represented in base-10/decimal.

To illustrate:

```
message: HELLO
ascii bytes: [72, 69, 76, 76, 79]
hex bytes: [0x48, 0x45, 0x4c, 0x4c, 0x4f]
base-16: 0x48454c4c4f
base-10: 310400273487
```
> Python's PyCryptodome library implements this with the methods bytes_to_long() and long_to_bytes(). You will first have to install PyCryptodome and import it with from Crypto.Util.number import *. For more details check the FAQ.


Convert the following integer back into a message:
```
11515195063862318899931685488813747395775516287289682636499965282714637259206269
```

## Write-Up
Di sini kita diajarkan soal big integers, casenya di sini adalah long (https://www.geeksforgeeks.org/cpp/difference-between-long-int-and-long-long-int-in-c-cpp/). Tugas kita adalah melakukan convert dari long menjadi bytes. Python punya library untuk case ini yaitu ```PyCryptodome``` yang bisa kita download dengan ```pip install```. Fungsinya adalah melakukan convert dari long menjadi bytes.

```
kurumi@LAPTOP-B49Q3K5D:/mnt/d/my-kisah/crypto/2.cryptohack/1.Introduction-to-CryptoHack/write-up/chall_6$ python3 solve.py 
crypto{3nc0d1n6_4ll_7h3_w4y_d0wn}
```
