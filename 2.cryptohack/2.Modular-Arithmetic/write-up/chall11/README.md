# Persamaan Kriptografi

$$
\begin{align*}
N &= p \cdot q \\
c_1 &\equiv (2 \cdot p + 3 \cdot q)^{e_1} \pmod{N} \\
c_2 &\equiv (5 \cdot p + 7 \cdot q)^{e_2} \pmod{N}
\end{align*}
$$

**Reduksi $c_1$ dan $c_2$ terhadap modulo $p$:**

$$
\begin{align*}
c_1 &\equiv (2 \cdot p + 3 \cdot q)^{e_1} \pmod{p} \\
c_1 &\equiv (0 + 3 \cdot q)^{e_1} \pmod{p} \\
c_1 &\equiv (3 \cdot q)^{e_1} \pmod{p}
\end{align*}
$$

$$
\begin{align*}
c_2 &\equiv (5 \cdot p + 7 \cdot q)^{e_2} \pmod{p} \\
c_2 &\equiv (0 + 7 \cdot q)^{e_2} \pmod{p} \\
c_2 &\equiv (7 \cdot q)^{e_2} \pmod{p}
\end{align*}
$$

**Manipulasi Eksponen untuk $c_1$:**

$$
\begin{align*}
c_1 &\equiv (3 \cdot q)^{e_1} \pmod{p} \\
c_1 &\equiv 3^{e_1} \cdot q^{e_1} \pmod{p} \\
c_1 \cdot (3^{e_1})^{-1} &\equiv 1 \cdot q^{e_1} \pmod{p} \\
(c_1 \cdot (3^{e_1})^{-1})^{e_2} &\equiv (1 \cdot q^{e_1})^{e_2} \pmod{p} \\
c_1^{e_2} \cdot 3^{-e_1 \cdot e_2} &\equiv q^{e_1 \cdot e_2} \pmod{p}
\end{align*}
$$

**Manipulasi Eksponen untuk $c_2$:**

$$
\begin{align*}
c_2 &\equiv (7 \cdot q)^{e_2} \pmod{p} \\
c_2 &\equiv 7^{e_2} \cdot q^{e_2} \pmod{p} \\
c_2 \cdot (7^{e_2})^{-1} &\equiv 1 \cdot q^{e_2} \pmod{p} \\
(c_2 \cdot (7^{e_2})^{-1})^{e_1} &\equiv (1 \cdot q^{e_2})^{e_1} \pmod{p} \\
c_2^{e_1} \cdot 7^{-e_2 \cdot e_1} &\equiv q^{e_2 \cdot e_1} \pmod{p}
\end{align*}
$$

**Eliminasi Persamaan:**

$$
\begin{align*}
c_1^{e_2} \cdot 3^{-e_1 \cdot e_2} &\equiv q^{e_1 \cdot e_2} \pmod{p} \\
c_2^{e_1} \cdot 7^{-e_2 \cdot e_1} &\equiv q^{e_2 \cdot e_1} \pmod{p} \\
\hline
c_1^{e_2} \cdot 3^{-e_1 \cdot e_2} - c_2^{e_1} \cdot 3^{-e_2 \cdot e_1} &\equiv 0 \pmod{p}
\end{align*}
$$

karena dalam matematika modulo, semisal ada A ≡ 0 mod p, dimana A,p ∈ ℤ maka A adalah kelipatan p.

Karena A dan N punya factor yang sama yaitu p. Kita bisa cek gcd(A,N) untuk dapat p, lalu N//p untuk dapat q
