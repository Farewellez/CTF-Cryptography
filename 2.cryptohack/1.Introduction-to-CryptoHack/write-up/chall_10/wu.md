# You either know, XOR you don't
I've encrypted the flag with my secret key, you'll never be able to guess it.
> Remember the flag format and how it might help you in this challenge!

```
0e0b213f26041e480b26217f27342e175d0e070a3c5b103e2526217f27342e175d0e077e263451150104

```

## Write-Up
Kita bisa implementasikan known plain text attack di challenge ini. Cara kerjanya adalah memanfaatkan kembali cara kerja dari operasi XOR yaitu reversible (https://eitca.org/quantum-information/eitc-qi-qif-quantum-information-fundamentals/introduction-to-quantum-computation/reversible-computation/examination-review-reversible-computation/how-can-the-xor-gate-be-considered-reversible-and-why-is-the-and-gate-not-reversible/). Artinya jika kita punya sembarang x dan y yang jika keduanya di XOR akan menghasilkan sembarang nilai z, maka jika kita balik melakukan XOR antara x dengan z maka kita bisa mendapatkan nilai y.

```
ct = [x1, x2, x3]
pt = [y1, y2, y3]

ct ⊕ key = pt
ct ⊕ pt = key
ct ⊕ pt = [x1, x2, x3] ⊕ [y1, y2, y3]
key = [x1, x2, x3] ⊕ [y1, y2, y3]
key = [x1 ⊕ y1, x2 ⊕ y2, x3 ⊕ y3]
```

Tapi kan, kita gatau pt? tentu saja tidak semua pt, tapi sebagian saja. Kita tau kalau prefix pt atau flag adalah ```crypto{```, _known pt_ inilah yang bisa kita gunakan untuk XOR ct untuk mendapatkan beberapa _known value_ dari key. 

```
(venv_linux) kurumi@LAPTOP-B49Q3K5D:/mnt/d/my-kisah/crypto/2.cryptohack/1.Introduction-to-CryptoHack/write-up/chall_10$ python3 solve.py 
crypto{1f_y0u_Kn0w_En0uGH_y0u_Kn0w_1t_4ll}
```