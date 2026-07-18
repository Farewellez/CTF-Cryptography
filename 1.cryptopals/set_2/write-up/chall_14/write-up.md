# Byte-at-a-time ECB decryption (Harder)
Take your oracle function from #12. Now generate a random count of random bytes and prepend this string to every plaintext. You are now doing:

AES-128-ECB(random-prefix || attacker-controlled || target-bytes, random-key)
Same goal: decrypt the target-bytes.

### Stop and think for a second.
What's harder than challenge #12 about doing this? How would you overcome that obstacle? The hint is: you're using all the tools you already have; no crazy math is required.

Think "STIMULUS" and "RESPONSE".

## Write-Up
Jadi di sini kita diberikan sebuah challenge #12 tapi versi lebih susah karena ada tambahan random prefix diawal, namun sebenarnya kebanyakan logic masih sama yaitu mulai dari mencari blocksize, cek apakah ini ECB, split menjadi block ukuran block size, lalu mencari repeated block ada di index block ke berapa untuk mengetahui secret prefix yang ditambahkan di oracle. Kerentanan utama, itu ada pada public variable ```KEY``` dan ```PREFIX``` yang statis, jadi kita bisa terus-terusan mengirim payload pt dan membuat kamus ct dari output oracle. Bedanya di challenge 12, ada di bagian residue yaitu bagaimana cara kita menemukan sisa payload yang mungkin berkumpul di ```PREFIX```. Contoh dari output ini:
```
ECB: True found repeated at block: 1
total same block: 2
payload length  : 41
residue         : 9
blocks ct       : [b'\xe7\xab\xfb9\x15\xfb\x01\xf1\x95\xfa\x969B\x00x\x12', b'\x05\x02\xfd\xa6@\xb7\xc7t\x84\x0e\xf4\x06\xd2\x00#\xcf', b'\x05\x02\xfd\xa6@\xb7\xc7t\x84\x0e\xf4\x06\xd2\x00#\xcf', b'\x17T\xaccC#\x02oI\xd4g(dW}l', b'\x1d\xb8\xe6Nk\xb8RO\xee)!4-{L\xf9', b'\x91\xba{I j;\x0c}O\xe2R\x10\xab@}', b'\xf2j\x99\x7fY\xad\x0e\x13g/\xe4\xe04tO\xf2', b'\xaf\xa6\xf9{\x91\xb9\xf7\x1b\x8f\n\xd2U@\xed\xc5\xf6', b'Cp\xd2\n&y\xf1t\xc1\xa8\xd3\xd9S\x90\xf3\xec', b'\xdc\xce\x7f\xc9f}\xc8\xc7\x00\xa4\xda\x94\xcd\xa3\x11.', b'\x08\x8aX<\xcf\x859{!\xb5\x86zRE\xb0\xaa', b'~x\x83\x9cm)z\x96\xb2pf\x9a\xb1\xe5\xe2t']
```
Kita dapat info kalau residue = 9, sedangkan payload length adalah 41, yaitu nilai dimana ECB terdeteksi dengan panjang payloads ```b'a'*41```. Lalu total same block ada 2 dengan repeated ditemukan di block 1, jadi total ada 2*16 byte yang sama sedangkan payload kita ada 41. Jika dihitung 41 - 32 = 9 yang nilainya sama seperti residue. Jadi, ada 9 byte nilai b'a' yang berkumpul membentuk block 0. Jadi secret prefix = 16 - 9 yaitu 7. Tapi yang digunakan di ```while loop``` nanti adalah ```b'a'*residue``` karena kita sudah tau butuh payload berjumlah 9 untuk mengisi block 1 yang adalah prefix sampah. Nantinya di while loop kita bisa fokus pada next block untuk melakukan iterasi byte per byte sampai byte ke-256 dan hingga suffix byte cipertext habis.
