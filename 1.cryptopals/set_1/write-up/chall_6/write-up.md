# Break repeating-key XOR
### It is officially on, now.
This challenge isn't conceptually hard, but it involves actual error-prone coding. The other challenges in this set are there to bring you up to speed. This one is there to qualify you. If you can do this one, you're probably just fine up to Set 6.

There's a file here. It's been base64'd after being encrypted with repeating-key XOR.

Decrypt it.

Here's how:

1. Let KEYSIZE be the guessed length of the key; try values from 2 to (say) 40.
2. Write a function to compute the edit distance/Hamming distance between two strings. The Hamming distance is just the number of differing bits. The distance between:
```
this is a test
```
and
```
wokka wokka!!!
```
is 37. Make sure your code agrees before you proceed.

3. For each KEYSIZE, take the first KEYSIZE worth of bytes, and the second KEYSIZE worth of bytes, and find the edit distance between them. Normalize this result by dividing by KEYSIZE.
4. The KEYSIZE with the smallest normalized edit distance is probably the key. You could proceed perhaps with the smallest 2-3 KEYSIZE values. Or take 4 KEYSIZE blocks instead of 2 and average the distances.
5. Now that you probably know the KEYSIZE: break the ciphertext into blocks of KEYSIZE length.
6. Now transpose the blocks: make a block that is the first byte of every block, and a block that is the second byte of every block, and so on.
7. Solve each block as if it was single-character XOR. You already have code to do this.
8. For each block, the single-byte XOR key that produces the best looking histogram is the repeating-key XOR key byte for that block. Put them together and you have the key.

This code is going to turn out to be surprisingly useful later on. Breaking repeating-key XOR ("Vigenere") statistically is obviously an academic exercise, a "Crypto 101" thing. But more people "know how" to break it than can actually break it, and a similar technique breaks something much more important.

### No, that's not a mistake.
We get more tech support questions for this challenge than any of the other ones. We promise, there aren't any blatant errors in this text. In particular: the "wokka wokka!!!" edit distance really is 37.

## Write-Up
Jadi di sini kita diberikan sebuah file yang didalamnya ada data yang terenkripsi dengan algoritma kriptografi repeated-key XOR lalu di encode dengan base64. Tugas kita adalah melakukan recover key dan mendekripsi pesan yang ada di file tersebut. Di awal kita bisa lakukan decode terlebih dahulu, lalu gabung menjadi 1 line encrypted byte utuh dengan ```"".join()```. Setelah itu, kita bisa coba guessing key dengan algoritma hamming distance (https://www.geeksforgeeks.org/dsa/concepts-of-hamming-distance/). Simplenya, hamming ini adalah teknik dimana kita melakukan pencocokan dengan mengidentifikasi tingkat bit dari 2 byte atau 2 variable. Di sini hal yang kita compare adalah block sepanjang keysize(yang kita asumsikan dari 2-40). Jadi ```block[i]``` dengan ```block[j]```, kemudian kita lakukan fixed XOR  keduanya untuk melihat output integer yang keluar. Kenapa XOR? karena hamming menghitung bit yang berbeda, maka kita bisa lakukan operasi XOR yang mana jika ada sembarang x, y ∈ ℤ ketika kita lakukan operasi XOR pada level bit, maka tiap bit yang menyusun dua integer tersebut akan di compare dan jika berbeda, maka akan bertambah 1. Contoh:
```
1110
0010
1101 = 3 bit berbeda
```

kurang lebih seperti itu konsep _hamming distance_. Anggaplah kita sudah ketemu kandidat _key size_ nya, lalu sekarang kita lakukan recover key dengan membuat sebuah block dari ciphertext dengan size dari key size. Jadi misal 1 block dengan panjang elemen 2, karena keysize nya yang ditebak adalah 2. Atau 1 block dengan panjang elemen 20, karena keysize nya yang ditebak adalah 20. Lalu tiap block ini akan di iterate dan dicocokkan dengan index ke-i dari key untuk di append ke list transpose. Jadi semua index ke-0 dari block akan masuk ke 1 kelompok, yaitu kelompok dengan index-0, index ke-1 dari block akan masuk ke 1 kelompok juga yaitu kelompok dengan index byte ke-1, dst. Baru dari situ kita iterate lagi transpose element yang sudah terkumpul untuk dilakukan operasi lain yaitu _single byte xor_.

Indahnya di sini, single byte xor yang biasanya digabung dengan function scoring tidak hanya efektif dalam sebuah sentence yang readable, tapi juga pada sebuah kandidat key yang mempunyai elemen ascii yang bisa dibaca. Ketika kita lakukan single byte xor dengan tiap byte dari block ke-i, kita juga akan simpan score tertinggi yang menjadi kandidat kemungkinan dari 1 byte kuncinya. Dari situ kita akan dapat kemungkinan key yang benar (INGAT: ini masih kemungkinan, jadi belum tentu benar karena ini juga menggunakan _letter frequency analyst_(https://en.wikipedia.org/wiki/Letter_frequency)).

Setelah dapat kandidat key dalam bentuk list, kita hanya perlu lakukan repeated key xor dengan operasi modulo pada len key untuk return sebuah plaintext yang bisa atau tidak bisa dibaca. Dari situ kita bisa analisis manual, mana hasil decrypt yang bisa dibaca dan mana yang tidak bisa dibaca lalu kita ubah slicing list pada ```for loop``` akhir dengan index ke-i dari readable sentence tersebut.
