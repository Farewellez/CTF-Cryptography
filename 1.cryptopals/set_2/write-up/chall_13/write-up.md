# ECB cut-and-paste
Write a k=v parsing routine, as if for a structured cookie. The routine should take:
```
foo=bar&baz=qux&zap=zazzle
```
... and produce:
```
{
  foo: 'bar',
  baz: 'qux',
  zap: 'zazzle'
}
```
(you know, the object; I don't care if you convert it to JSON).

Now write a function that encodes a user profile in that format, given an email address. You should have something like:
```
profile_for("foo@bar.com")
```

... and it should produce:
```
{
  email: 'foo@bar.com',
  uid: 10,
  role: 'user'
}
```
... encoded as:
```
email=foo@bar.com&uid=10&role=user
```

Your "profile_for" function should not allow encoding metacharacters (& and =). Eat them, quote them, whatever you want to do, but don't let people set their email address to "foo@bar.com&role=admin".

Now, two more easy functions. Generate a random AES key, then:<br>
A. Encrypt the encoded user profile under the key; "provide" that to the "attacker".<br>
B. Decrypt the encoded user profile and parse it.<br>
Using only the user input to profile_for() (as an oracle to generate "valid" ciphertexts) and the ciphertexts themselves, make a role=admin profile.

## Write-Up
ECB cut-and-paste mengambil nama dari bagaimana cara kita memanfaatkan vulnerability yang ada pada sistem (karena kita yang membuatnya juga lol). Dalam challenge ini tujuan kita adalah melakukan sebuah decrypt terhadap sebuah encoded profile yang mana, kita harus mengubah ```role=user``` menjadi ```role=admin```. Tapi, bagaimana caranya? ya kita perlu memanfaatkan function ```profile_for()``` dan ```profile_encrypt()``` untuk menghasilkan 2 buah ciphertext:
1. Ciphertext pertama untuk bagian email=foo@bar.com&uid=10&role=....
2. Ciphertext kedua untuk mendapatkan bagian admin+padding pkcs#7

Jadi anggaplah di sini kita ada 2 kali sending payload ke sistem. Kita coba dulu hitung untuk payload pertama: 
email=  | 6 <br>
[email] | x <br>
&uid=   | 5 <br>
[uid]   | 2 <br>
&role=  | 6 <br>
total = 19 + x <br>
x + 19 ≡ 0 (mod 16) <br>
x = 13 <br>
email=&uid=10&role= <br>
Jadi total ada 13 email value yang bisa kita kirim untuk menghilangkan sampah string ```user```. Contoh di sini aku pakai:
```
spoof1 = 'a'*13
gmail_spoof1 = profile_for(spoof1)
enc_spoof1 = profile_encrypt(gmail_spoof1.encode())
dec_spoof1 = profile_decrypt(enc_spoof1)
print(f"email            : {gmail_spoof1}")
print(f"profile          : {enc_spoof1}")
print(f"decrypted profile: {dec_spoof1}")
print(gmail_spoof1[:32])
```
pasti keluar salah satunya di printout terakhir yaitu ```email=aaaaaaaaaaaaa&uid=10&role=```. Hasil enkripsi dari 32 byte pertama inilah yang bakal kita ambil untuk block 1 dan block 2 nanti.
> Note: akan ada 3 block target yaitu 2 block 32 byte dari payloads 1 dan 1 block 16 byte dari payloads 2

Setelah selesai di payload pertama, lanjut ke payload kedua. Ada masalah sebenarnya yaitu kita perlu mengambil hasil enkripsi dari ```admin``` saja, tapi hal ini sebenarnya simple. Kita tinggal buat bagaimana caranya byte "admin" ada di awal block dan kita bisa pakai sisanya untuk padding. Misal, admin sendiri kan punya panjang string = 5, jadi kita coba hitung 16 - 5 = 11. Jadi kita butuh padding 11 untuk membuat 1 block yang berisi encrypted byte admin. Jadi kita bisa hitung untuk payload ke-2:
email=  | 6 <br>
[email] | a*10 = 10 <br>
admin   | 5 <br>
padd    | y <br>
y = 11 pkcs#7 <br>
Kenapa a di sini 10? sedangkan a di payload 1 tadi ada 13? ya karena kita menyesuaikan agar di sini, block 1 terisi 16 byte penuh sehingga "admin" tepat berada di awal block 2. 
```
spoof2 = 'a'*10 + "admin" + '\x0b'*11
gmail_spoof2 = profile_for(spoof2)
enc_spoof2 = profile_encrypt(gmail_spoof2.encode())
dec_spoof2 = profile_decrypt(enc_spoof2)
print(f"email            : {gmail_spoof2.encode()}")
print(f"profile          : {enc_spoof2}")
print(f"decrypted profile: {dec_spoof2}")
print(gmail_spoof2[16:32].encode())
```
Bakal dapat: ```b'admin\x0b\x0b\x0b\x0b\x0b\x0b\x0b\x0b\x0b\x0b\x0b'``` <br>
Selanjutnya, finalisasi untuk menggabungkan kedua payload
```
# concenate
admin = enc_spoof2[16:32]
# print(len(gmail_spoof2[16:32].encode()))
final_spoof = enc_spoof1[:32] + admin
# print(len(final_spoof)%16)
decrypt_spoof = profile_decrypt(final_spoof)
print(decrypt_spoof)
```
Di sini kita berhasil dapat sebuah decrypted profile dengan role admin dan sukses untuk mengabaikan filter di function ```profile_for``` (sebenarnya mengabaikan kurang tepat, kita lebih ke memanfaatkan saja celah cut-and-paste nya). Hasil outputnya adalah cookies seperti ini:
```
{'email': 'aaaaaaaaaaaaa', 'uid': '10', 'role': 'admin'}
```
