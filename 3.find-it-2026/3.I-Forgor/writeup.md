# Write-up: I Forgor

## Informasi Soal

- **Challenge**: I Forgor
- **Kategori**: Crypto
- **Poin**: 100
- **Author**: imios

Deskripsi singkat challenge:

> George droid hendak pulang kembali ke agartha setelah bekerja di kebun sawitnya, di tengah perjalanannya kembali ke agartha, dia lupa secret phrase untuk masuk ke agratha, namun bahlinus, si penjaga pintu agartha, tau droid suka lupa, jadi dia memberi droid catatan berisi sandi aneh, RSA modulus, yang berisikan secret phrasenya.

File yang diberikan hanya satu:

- `Release.txt`

Isinya:

```text
# Catatan Bahlinus untuk George Droid
# Secret Phrase terenkripsi di bawah ini:

n = 23970220268504018898939762145558941011501625979207865682859186638421876523999912061291880905436660142345853247070514127024479901460394017772740266005230978703117565707755364136423230491039863481699967667954546559385311099683935515250485966453702172776887556942953259837072545191834169557438406560085885060856983084807490214435941914995543788266398904571060010903348616239169602410712762744093863499426569724103135914588720197773229864239864200677138332303023246726917616654877399824641680979401494954004901966557878363717274443194093952771239965030386616016625442750346363777085750059158090124976767670984180436034177

e1 = 3
c1 = 48514981442167735398664157778393529344445831627932640242131908290299696245389650423049156372562540306206000007802445873770177969396340156903511874404060868351586526135649964175510444342265007553907711462492193565011663471015682882586790757989938743171358055663675043635581561026038338947477641217036496944063259461971701331711130638519175239148496464528439366118434407981512404090008585648835158674514338450143891461624606275727192837339180998829029670877903845620803522204648177573615469324521401344265636043135245802280209503418578726871038290940989392261621379361625906371302450375932975945898335345719369986420512141517036214131

e2 = 65537
c2 = 163749454157582570085023594094195159846663264627999849553782161730622543315629168925203002234053706037302256241908920197773229864239864200677138332303023246726917616654877399824641680979401494954004901966557878363717274443194093952771239965030386616016625442750346363777085750059158090124976767670984180436034177727402660052309787031175657077553641364232304910398634816999676679545465593853110996839355152504859664537021727768875569429532598370725451918341695574384065600858850608569830848074902144359419149955437882663989045710600109033486162391696024107127627440
```

---

## Observasi Awal

Sekilas ini terlihat seperti skenario RSA dengan:

- modulus `n`
- dua public exponent: `e1 = 3` dan `e2 = 65537`
- dua ciphertext: `c1` dan `c2`

Hipotesis paling natural adalah:

1. plaintext yang sama dienkripsi dua kali dengan modulus yang sama
2. eksponen berbeda
3. intended attack: **common modulus attack**

Karena:

- `gcd(3, 65537) = 1`

Kalau semua nilainya valid, maka kita bisa mencari koefisien Bezout:

```text
a * e1 + b * e2 = 1
```

lalu memulihkan:

```text
m = c1^a * c2^b mod n
```

Namun setelah dicek lebih jauh, data challenge ternyata tidak konsisten.

---

## Cek Konsistensi Data

### 1. `c1` lebih besar dari `n`

Panjang digit:

- `len(n) = 617`
- `len(c1) = 632`
- `len(c2) = 564`

Pada RSA biasa, ciphertext adalah hasil:

```text
c = m^e mod n
```

sehingga **selalu** berlaku:

```text
0 <= c < n
```

Tetapi di sini `c1 > n`, jadi `c1` bukan ciphertext RSA modular yang valid.

### 2. `c2` terlihat korup

Bagian akhir `c2` ternyata identik dengan substring panjang dari `n`. Ini sangat tidak wajar untuk ciphertext RSA acak.

Artinya besar kemungkinan:

- `c2` terpotong
- atau salah copy-paste
- atau file release yang diberikan memang rusak

### 3. `c1` juga tidak konsisten secara modular

Setelah modulus `n` difaktorkan sebagian, saya cek apakah `c1 mod p` merupakan cubic residue untuk faktor-faktor kecil `n`.

Hasilnya:

- modulo `769`: ada akar kubik
- modulo `2757119`: ada akar kubik
- modulo `1579`: **tidak ada akar kubik**

Kalau `c1` benar-benar berasal dari:

```text
c1 = m^3 mod n
```

maka `c1` harus punya akar kubik modulo **setiap** faktor prima dari `n`. Karena ini gagal di `1579`, berarti `c1` juga tidak valid sebagai ciphertext RSA dengan `e = 3`.

Kesimpulan penting:

> Artefak yang diberikan tidak cukup konsisten untuk merecover plaintext/flag final secara kriptografis.

---

## Arah Serangan yang Masih Bisa Diambil

Walaupun ciphertext bermasalah, modulus `n` sendiri ternyata lemah.

Saya mulai dengan pendekatan umum:

- cek `gcd`
- cek kemungkinan perfect power
- brute small factor
- coba `Pollard p-1`
- cek database faktor publik

Ternyata `n` langsung punya faktor kecil yang bisa diambil.

---

## Faktorisasi `n`

Dengan `Pollard p-1` didapat faktor:

```text
1214251
```

Lalu setelah dicek:

```text
1214251 = 769 * 1579
```

Faktor berikutnya yang jatuh:

```text
2757119
```

Verifikasi melalui FactorDB memberi hasil:

```text
n = 769 * 1579 * 2757119 * C604
```

dengan:

- `C604` = kofaktor komposit 604 digit yang belum terfaktor penuh

Jadi modulusnya **bukan** produk dua prima besar seperti RSA sehat, melainkan punya beberapa faktor kecil yang sangat mudah ditemukan.

Ini sudah cukup untuk menyimpulkan bahwa intended weakness dari modulus tersebut adalah:

> **RSA modulus lemah terhadap faktorisasi, khususnya lewat Pollard p-1 / small factors**

---

## Reproduksi Singkat

Contoh skrip Python untuk menemukan faktor kecil dengan `Pollard p-1`:

```python
import math

n = 23970220268504018898939762145558941011501625979207865682859186638421876523999912061291880905436660142345853247070514127024479901460394017772740266005230978703117565707755364136423230491039863481699967667954546559385311099683935515250485966453702172776887556942953259837072545191834169557438406560085885060856983084807490214435941914995543788266398904571060010903348616239169602410712762744093863499426569724103135914588720197773229864239864200677138332303023246726917616654877399824641680979401494954004901966557878363717274443194093952771239965030386616016625442750346363777085750059158090124976767670984180436034177

def pollard_pm1(n, B=50000):
    a = 2
    for j in range(2, B + 1):
        a = pow(a, j, n)
        if j % 1000 == 0:
            g = math.gcd(a - 1, n)
            if 1 < g < n:
                return g
    g = math.gcd(a - 1, n)
    if 1 < g < n:
        return g
    return None

f = pollard_pm1(n)
print(f)
```

Output:

```text
1214251
```

Lalu:

```python
f = 1214251
print(n % f == 0)
print(1214251 == 769 * 1579)
```

Output:

```text
True
True
```

Dan dari cek lanjutan:

```text
2757119
```

juga merupakan faktor dari `n`.

---

## Kenapa Flag Tidak Bisa Dipastikan?

Secara normal, setelah `n` difaktorkan kita berharap bisa:

1. menghitung `phi(n)` atau `lambda(n)`
2. membalik `e`
3. mendekripsi ciphertext
4. memperoleh plaintext/flag

Namun untuk challenge ini, langkah itu gagal karena data ciphertext tidak valid:

- `c1 > n`
- `c2` tampak terpotong/korup
- `c1` tidak kompatibel dengan bentuk `m^3 mod n`

Jadi problem-nya bukan sekadar "faktor belum lengkap", tetapi memang **artefak release-nya tidak cukup konsisten untuk dekripsi final**.

---

## Kesimpulan

Hal yang berhasil dibuktikan dari challenge:

1. Modulus RSA `n` lemah dan memiliki faktor kecil.
2. Faktor yang berhasil diverifikasi:

```text
n = 769 * 1579 * 2757119 * C604
```

3. Teknik yang relevan:
   - faktorisasi modulus
   - `Pollard p-1`
4. Artefak ciphertext pada `Release.txt` tidak konsisten, sehingga flag final tidak dapat direcover secara unik dari file yang diberikan.

Kalau challenge ini memang intended sebagai RSA break murni, kemungkinan besar:

- file release aslinya berbeda
- atau salah satu/celah ciphertext terpotong saat distribusi

---

- gaya CTFtime
- gaya blog teknis
- versi Bahasa Inggris
- versi dengan snippet solver terpisah
