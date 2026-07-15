# Fixed XOR
Write a function that takes two equal-length buffers and produces their XOR combination.

If your function works properly, then when you feed it the string:
```
1c0111001f010100061a024b53535009181c
```

... after hex decoding, and when XOR'd against:
```
686974207468652062756c6c277320657965
```

... should produce:
```
746865206b696420646f6e277420706c6179
```

## Write-Up
Di sini kita perlu membuat sebuah fixed xor function yang akan menerima 2 argument. Untuk argument awal aku sengaja menetapkan string sebagai tipe data parameter karena encoding string nantinya akan dilakukan di dalam function. Meskipun opsional, di awal function kita bisa buat sebuah case dimana ketika panjang string dari 2 parameter itu tidak sama, karena kita akan melakukan operasi XOR dengan syarat kedua variable yang di operasikan itu memiliki panjang sama.  

Setelah itu, kita bisa menggunakan _list comprehension_ untuk operasi XOR antara 2 variable di parameter yang di encode terlebih dahulu dari hex -> bytes, lalu gunakan zip method untuk iterate keduanya. Setelah itu baru lakukan XOR di tiap byte dan casting ke hex method untuk ubah menjadi hex. Di akhir, kita bisa return dengan ```"".join``` method agar isi dari ciphertext hex menjadi 1 string utuh dan bukan dalam bentuk list lagi.
