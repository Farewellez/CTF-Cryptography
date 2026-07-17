# Detect AES in ECB mode
In this file are a bunch of hex-encoded ciphertexts.

One of them has been encrypted with ECB.

Detect it.

Remember that the problem with ECB is that it is stateless and deterministic; the same 16 byte plaintext block will always produce the same 16 byte ciphertext.

## Write-Up
Simple saja, kita coba iterate tiap line yang ada di dalam file, lalu coba convert dari hex string menjadi bytes dulu. Karena dari deskripsi kita diberi hint "the same 16 byte plaintext block will always produce the same 16 byte ciphertext", jadi kita buat blocks yang mengambil elemen lompatan 16. Contoh:
```
blocks = [ciphertext[i:i+16] for i in range(0, len(ciphertext), 16)]
```

Setelah itu kita cukup casting type menjadi ```set``` dan kita cek, apakah length list asli dan length list yang diubah ke ```set``` berbeda. Jika iya, maka bisa dipastikan line ciphertext tersebut dienkripsi dengan AES ECB.
