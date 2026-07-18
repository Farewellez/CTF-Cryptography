# Implement CBC mode
CBC mode is a block cipher mode that allows us to encrypt irregularly-sized messages, despite the fact that a block cipher natively only transforms individual blocks.

In CBC mode, each ciphertext block is added to the next plaintext block before the next call to the cipher core.

The first plaintext block, which has no associated previous ciphertext block, is added to a "fake 0th ciphertext block" called the initialization vector, or IV.

Implement CBC mode by hand by taking the ECB function you wrote earlier, making it encrypt instead of decrypt (verify this by decrypting whatever you encrypt to test), and using your XOR function from the previous exercise to combine them.

The file here is intelligible (somewhat) when CBC decrypted against "YELLOW SUBMARINE" with an IV of all ASCII 0 (\x00\x00\x00 &c)

### Don't cheat.
Do not use OpenSSL's CBC code to do CBC mode, even to verify your results. What's the point of even doing this stuff if you aren't going to learn from it?

## Write-Up
Di sini kita dapat sebuah pesan di dalam .txt file yang dienkripsi menggunakan AES CBC (https://www.geeksforgeeks.org/ethical-hacking/block-cipher-modes-of-operation/). Kita diminta untuk melakukan decrypt pada isi file tersebut. Karena CBC melakukan XOR antar block sebelum di enkripsi dengan ```AES_ECB```, jadi kita hanya perlu menggunakan ```AES.new(key,MODE_ECB)``` tanpa mode CBC. Kita perlu decode dulu dari base64 lalu gabung menjadi 1 line, sebenarnya bebas bisa menggunakan readlines atau mau digabung dengan ```"".join()```, cuman di sini aku lebih nyaman langsung ku gabung karena ini sebenarnya adalah 1 liner ciphertext.

Setelah itu, kita pisah menjadi block-block dengan 1 block punya total 16 bytes elemen. Di deskripsi soal sudah dijelaskan _"fake 0th ciphertext block" called the initialization vector, or IV_. Jadi block index-0 (0 indexed) perlu di decrypt dengan key ```b"YELLOW SUBMARINE"``` kemudian di XOR dengan ```iv```. Di index ke-1 ciphertext, berbeda dengan sebelumnya yang di XOR dengan iv, setelah kita decrypt dengan key ```b"YELLOW SUBMARINE"``` kita XOR hasil decrypt tersebut dengan ciphertext index ke-0 sebelumnya, begitu seterusnya hingga length ciphertext habis dan kita akan mendapatkan pesan yang terenkripsi.
