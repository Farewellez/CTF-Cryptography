# CBC bitflipping attacks
Generate a random AES key.

Combine your padding code and CBC code to write two functions.

The first function should take an arbitrary input string, prepend the string:
```
"comment1=cooking%20MCs;userdata="
```
.. and append the string:
```
";comment2=%20like%20a%20pound%20of%20bacon"
```
The function should quote out the ";" and "=" characters.

The function should then pad out the input to the 16-byte AES block length and encrypt it under the random AES key.

The second function should decrypt the string and look for the characters ";admin=true;" (or, equivalently, decrypt, split the string on ";", convert each resulting string into 2-tuples, and look for the "admin" tuple).

Return true or false based on whether the string exists.

If you've written the first function properly, it should not be possible to provide user input to it that will generate the string the second function is looking for. We'll have to break the crypto to do that.

Instead, modify the ciphertext (without knowledge of the AES key) to accomplish this.

You're relying on the fact that in CBC mode, a 1-bit error in a ciphertext block:
- Completely scrambles the block the error occurs in
- Produces the identical 1-bit error(/edit) in the next ciphertext block.

### Stop and think for a second.
Before you implement this attack, answer this question: why does CBC mode have this property?

## Write-Up
Di sini kita diminta untuk melakukan bit-flipping attack. Ini sebenarnya mirip dengan case cut-and-paste cuman yang diubah disini adalah bagian byte tertentu dari ciphertext. Inti dari vulnerability yang ada pada bagaimana key bersifat statis lalu iv yang tetap pada 16 byte awal ciphertext. Jadi kita perlu add something payload ke dalam oracle terlebih dahulu untuk mendapatkan sebuah ciphertext, tujuan akhir kita bagaimana caranya ";admin=true;" ada pada hasil decrypt. Masalahnya, "=" dan ";" akan selalu ter-quote. Jadi bagaimana caranya? kita butuh melakukan manipulasi pada hasil ciphertext, namun tidak pada prefix atau suffix yang di add di oracle, melainkan pada payload kita sendiri. Rumus yang aku pakai setelah mengumpulkan ct dan membentuk block 16 byte:
test_block = [ct[i:i+16] for i in range(16, len(ct), 16)]
```
# print()
# for block in test_block:
#     print(block)

# print()
# print(dec_pt)

# block0: comment1=cooking
# block1: %20MCs;userdata=
# block2: aaaaaaaaaaaaaaaa
# block3: :admin:true:;com -> 0, 6, 11
# block4: ment2=%20like%20
# ...
# ct0 = block0 xor iv
# ct1 = block1 xor ct0
# ct2 = block2 xor ct1
# ct3 = block3 xor ct2 -> payload
# somehow in decrypt function
# pt1 = ct0 xor iv
# pt2 = ct1 xor ct0
# pt3 = ct2 xor ct1
# so if we try modifying ct2 output, it will affect on pt3

# ct2 = 16*2 = 32
```
Jadi terlihat, target kita itu adalah 16 byte yang mengandung "admin" string. Cuman, Jika kita cek bagaimana cara kerja AES CBC, block3 itu digunakan di ```ct3 = block3 xor ct2```. Artinya apa? ya ini ada hubungannya dengan ct2 yaitu tempat payload kita berada (16 byte payload lebih tepatnya). Lalu kita lanjut ke mekanisme decryptnya, fokus pada bagian ```pt3 = ct2 xor ct1```, lihat? kalau ternyata pt3 atau tempat admin berada itu bisa terdampak kalau kita mengubah antara ct2 atua ct1. Namun, kita tau kalau payload kita itu ada di block2 yang merupakan bahan untuk ct2, jadi bagian ciphertext yang bisa kita ubah yaitu ct ke-2 atau block ke-2 dari indexed 0. Karena itu pada bagian ini
```
# ct2 = 16*2 = 32
modif_ct = bytearray(test_block[2])
modif_ct[0] ^= 0x1
modif_ct[6] ^= 0x7
modif_ct[11] ^= 0x1
test_block[2] = bytes(modif_ct)
```
Kita mengambil ```test_block[2]``` yang mana ```test_block``` sendiri merupakan kumpulan block dari ciphertext dengan ukuran block size 16 byte. Untuk melakukan bit flipping, maka kita perlu cek dulu target byte yang akan di XOR. Bisa coba dengan ini:
```
>>> ord(':') ^ ord(';')
1
>>> ord(':') ^ ord('=')
7
>>> 
```
Sekarang kita tau, ":" agar menjadi ";" perlu di XOR dengan 1 atau 0x1 dan ":" agar menjadi "=" perlu di XOR dengan 7 atau 0x7. Mungkin ada yang bertanya, kenapa ga langsung replace saja misal byte ":" dengan byte ";". Untuk mengetahui ini, kita harus balik ke bagian sini ```ct3 = block3 xor ct2 -> payload```. Di sini, kita tau kalau block3 target kita di XOR dengan ct2 atau ct sebelumnya untuk menghasilkan ct3, lalu di sini ```pt3 = ct2 xor ct1``` kita tidak tau hasil deskripsi XOR AES dengan ct sebelumnya, yang bisa kita kendalikan hanya di ct2 dan plaintext asli. Masih agak rumit? bisa cek ini.

Masuk ke bit-flippingnya, kita tau dari rumus decrypt: 
```
O = D(Ci) XOR Ci-1
```
dengan O = original pt; C adalah ct. Lalu, bagaimana jika kita ingin memanipulasi O? tentu kita tidak bisa langsung memanipulasi Ci-1 sesuka hati kan? karena bahkan D(Ci) aja kita gatau gimana itu decryptnya pake key juga. Jadi kita perlu sebuah aksen Ci anggaplah Ci versi modified dan Pt` modified. Anggap nilai y di bawah ini adalah value yang perlu di XOR dengan ciphertext
```
Pt` = D(Ci) XOR (Ci-1 XOR y)
memanfaatkan sifat asosiatif XOR
Pt` = (D(Ci) XOR Ci-1) XOR y
get it?
Pt` = O XOR y
```
dan perubahan yang dilakukan di ciphertext akan muncul sama persis dengan pt Orinya, karena itu kita perlu blit-flipping dan tanpa perlu tau key dari AES nya dengan syarat keynya statis dan kita tau target dari byte yang akan kita flipped.
