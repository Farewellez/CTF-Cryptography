# Base64
Another common encoding scheme is Base64, which allows us to represent binary data as an ASCII string using an alphabet of 64 characters. One character of a Base64 string encodes 6 binary digits (bits), and so 4 characters of Base64 encode three 8-bit bytes.

Base64 is most commonly used online, so binary data such as images can be easily included into HTML or CSS files.

Take the below hex string, decode it into bytes and then encode it into Base64.

```
72bca9b68fc16ac7beeb8f849dca1d8a783e8acf9679bf9269f7bf
```

> In Python, after importing the base64 module with import base64, you can use the base64.b64encode() function. Remember to decode the hex first as the challenge description states.

## Write-Up
Di sini kita diminta untuk melakukan decode hex -> bytes lalu kita decode dengan base64 (https://en.wikipedia.org/wiki/Base64). Kita bisa menggunakan method python ```base64.b64encode()``` untuk melakukan decode bytes.

```
kurumi@LAPTOP-B49Q3K5D:/mnt/d/my-kisah/crypto/2.cryptohack/1.Introduction-to-CryptoHack/write-up/chall_5$ python3 solve.py 
crypto{Base_64_Encoding_is_Web_Safe}
```