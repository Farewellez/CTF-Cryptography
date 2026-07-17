# AES in ECB mode
The Base64-encoded content in this file has been encrypted via AES-128 in ECB mode under the key
```
"YELLOW SUBMARINE".
```
(case-sensitive, without the quotes; exactly 16 characters; I like "YELLOW SUBMARINE" because it's exactly 16 bytes long, and now you do too).

Decrypt it. You know the key, after all.

Easiest way: use OpenSSL::Cipher and give it AES-128-ECB as the cipher.

### Do this with code.
You can obviously decrypt this using the OpenSSL command-line tool, but we're having you get ECB working in code for a reason. You'll need it a lot later on, and not just for attacking ECB.

## Write-Up
Di sini lebih gampang challnya ketimbang chall yang ke-6 karena tidak banyak operasi yang kita buat dengan custom function, tapi lebih ke pemanfaatan library Python Cryptography Toolkit contoh (https://pypi.org/project/pycryptodome/). Seperti chall sebelumnya, di awal kita decode dulu isi dari file 7.txt dan kita jadikan one line dengan ```"".join()```. Kemudian kita import AES dari class ```Crypto.Cipher```. Dari situ kita buat sebuah object dengan parameter _ECB mode_ (sesuai perintah soal). Setelah kita kita hanya perlu panggil method decrypt dari object class tadi dan input argumetn ciphertext kita. Nanti hanya perlu ```decode()``` outputnya agar bisa convert dari bytes -> string yang readable.
