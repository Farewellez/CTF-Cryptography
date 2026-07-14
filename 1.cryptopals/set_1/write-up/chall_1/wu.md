# Convert hex to base64
The string:

```
49276d206b696c6c696e6720796f757220627261696e206c696b65206120706f69736f6e6f7573206d757368726f6f6d
```
Should produce:

```
SSdtIGtpbGxpbmcgeW91ciBicmFpbiBsaWtlIGEgcG9pc29ub3VzIG11c2hyb29t
```
So go ahead and make that happen. You'll need to use this code for the rest of the exercises.

### Cryptopals Rule
Always operate on raw bytes, never on encoded strings. Only use hex and base64 for pretty-printing.

## Write-Up
Jadi kita diberikan sebuah hex string di sini. Daru rules yang ada, kita diminta untuk melakukan operasi pada raw bytes. Cara mengubah hex string -> raw bytes di python bisa dengan ```bytes.fromhex()```. Setelah itu, kita menggunakan module base64 yang bisa kita import, lalu menggunakan method base64.b64encode(bytes) untuk menghasilkan sebuah encoded bytes base64. Di akhir, untuk mencetak output persis, kita gunakan ```decode()``` method bawaan string untuk casting type dari bytes -> string
