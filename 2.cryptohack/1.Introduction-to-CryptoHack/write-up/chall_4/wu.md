# Hex
When we encrypt something the resulting ciphertext commonly has bytes which are not printable ASCII characters. If we want to share our encrypted data, it's common to encode it into something more user-friendly and portable across different systems.

Hexadecimal can be used in such a way to represent ASCII strings. First each letter is converted to an ordinal number according to the ASCII table (as in the previous challenge). Then the decimal numbers are converted to base-16 numbers, otherwise known as hexadecimal. The numbers can be combined together, into one long hex string.

Included below is a flag encoded as a hex string. Decode this back into bytes to get the flag.

63727970746f7b596f755f77696c6c5f62655f776f726b696e675f776974685f6865785f737472696e67735f615f6c6f747d

> In Python, the bytes.fromhex() function can be used to convert hex to bytes. The .hex() instance method can be called on byte strings to get the hex representation.

Resources:
  - <a href="https://www.rapidtables.com/code/text/ascii-table.html"> ASCII table </a>
  - <a href="https://en.wikipedia.org/wiki/Hexadecimal"> Wikipedia: Hexadecimal </a>

## Write-Up
Untuk bagian sesi ini, kita diberitau soal ```hex```, yaitu angka basis 16 yang biasa digunakan di bidang cryptography juga. Kita bisa convert semua hal ke layer byte yang lebih mudah untuk dioperasikan. Karena nanti kita akan sering melakukan operasi dalam bentuk bytes, jadi kita bisa convert hex -> bytes dengan method ```bytes.fromhex()``` di python.

```
kurumi@LAPTOP-B49Q3K5D:/mnt/d/my-kisah/crypto/2.cryptohack/1.Introduction-to-CryptoHack/write-up/chall_4$ python3 solve.py 
crypto{You_will_be_working_with_hex_strings_a_lot}
```
