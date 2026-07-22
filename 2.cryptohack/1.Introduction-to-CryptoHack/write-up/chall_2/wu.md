# Great Snakes
Modern cryptography involves code, and code involves coding. CryptoHack provides a good opportunity to sharpen your skills.

Of all modern programming languages, Python 3 stands out as ideal for quickly writing cryptographic scripts and attacks. For more information about why we think Python is so great for this, please see the FAQ.

Run the attached Python script and it will output your flag.

Challenge files:
  - <a href="https://cryptohack.org/static/challenges/great_snakes_35381fca29d68d8f3f25c9fa0a9026fb.py"> great_snakes.py </a>

Resources:
  - <a href="https://wiki.python.org/moin/BeginnersGuide/Download"> Downloading Python </a>

## Write-Up
Jadi di sini cryptohack memberi sebuah pesan tersirat kalau misal python3 adalah bahasa yang disarankan untuk cryptography. Kita juga diberikan sebuah script py yang digunakan untuk decrypt flag dengan operasi bitwise XOR dengan key ```0x32```. Coba jalankan dan kita dapat flagnya.
```
kurumi@LAPTOP-B49Q3K5D:/mnt/d/my-kisah/crypto/2.cryptohack/1.Introduction-to-CryptoHack/write-up/chall_2$ python3 solve.py 
Here is your flag:
crypto{z3n_0f_pyth0n}
```
