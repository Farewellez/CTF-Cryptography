# Caesar Cipher

- **Kategori:** Crypto
- **Poin:** 50
- **Author:** mojitodev

## Deskripsi

Diberikan sebuah file `ciphertext.txt` yang berisi pesan terenkripsi. Dari judul challenge, sudah terlihat kuat bahwa enkripsi yang dipakai adalah **Caesar cipher**.

## File yang diberikan

Isi `ciphertext.txt`:

```text
Ymnx nx f xjhwjy ymj vzny htzw fyyjw. Qnkj ymj bnqq gj f xjhtsi bj bnqq gjfyyj,
jshwduynts ymj knwxy ts ymj xtrj tk ymj ufxxfrrnsl gjktwj. Tzlm rjxxflj, ymj
htsyfsy tk ymj xtrj qnkj f hfjxfw ns yjcy. Qjilmynts ymj jshwduy rjxxflj kwtr
f wjfi ymj rjxxflj yt ymj fxyjw. Rjxxflj xynsl ymnx KnsiNYHYK{Mrrrr_1_W89qqd_i5sy_pstb_Ym8_U5xxbtwi}
```

## Analisis

Caesar cipher bekerja dengan menggeser setiap huruf sejumlah nilai tetap. Karena hanya ada 26 kemungkinan shift, cara paling cepat adalah brute force semua shift sampai muncul plaintext yang masuk akal.

Salah satu hasil brute force yang valid adalah **shift 5**:

```text
This is a secret the quit cour atter. Life the will be a second we will beatte,
encryption the first on the some of the passamming before. Ough message, the
contant of the some life a caesar in text. Ledghtion the encrypt message from
a read the message to the aster. Message sting this FindITCTF{Hmmmm_1_R89lly_d5nt_know_Th8_P5ssword}
```

Walaupun kalimat pembukanya tidak sepenuhnya rapi, bagian flag terlihat jelas dan konsisten dengan format CTF.

## Solusi

Brute force Caesar cipher dengan shift `5`, atau setara dengan menggeser setiap huruf ciphertext **mundur 5 karakter**.

Contoh script Python:

```python
import string

s = open("ciphertext.txt").read()
alpha = string.ascii_lowercase
ALPHA = string.ascii_uppercase

shift = 5
out = []

for ch in s:
    if ch in alpha:
        out.append(alpha[(alpha.index(ch) - shift) % 26])
    elif ch in ALPHA:
        out.append(ALPHA[(ALPHA.index(ch) - shift) % 26])
    else:
        out.append(ch)

print("".join(out))
```

## Flag

```text
FindITCTF{Hmmmm_1_R89lly_d5nt_know_Th8_P5ssword}
```
