def solve_binary_table(n):
    # n dalam bentuk biner (panjang 9-bit untuk n=391)
    n_bin = [int(b) for b in bin(n)[2:]][::-1]  # bit 2^0 sampai 2^8

    print(f"Target N = {n} (Biner LSB-ke-MSB: {n_bin})\n")

    # Ruang pencarian bit internal: p = (1, p3, p2, p1, 1), q = (1, q3, q2, q1, 1)
    for p1 in [0, 1]:
        for p2 in [0, 1]:
            for p3 in [0, 1]:
                for q1 in [0, 1]:
                    for q2 in [0, 1]:
                        for q3 in [0, 1]:
                            p_bits = [1, p1, p2, p3, 1]
                            q_bits = [1, q1, q2, q3, 1]

                            # Evaluasi per kolom sesuai penjumlahan parsial + carry
                            carry = 0
                            valid = True

                            for col in range(len(n_bin)):
                                # Jumlahkan perkalian parsial p_i * q_j pada kolom tersebut
                                partial_sum = sum(
                                    p_bits[i] * q_bits[col - i]
                                    for i in range(5)
                                    if 0 <= (col - i) < 5
                                )
                                total = partial_sum + carry

                                bit_result = total % 2
                                carry = total // 2

                                if bit_result != n_bin[col]:
                                    valid = False
                                    break

                            if valid and carry == 0:
                                p_val = sum(b * (2**i) for i, b in enumerate(p_bits))
                                q_val = sum(b * (2**i) for i, b in enumerate(q_bits))
                                print(
                                    f"Ditemukan solusi:\n"
                                    f"  p = {p_bits[::-1]} -> {p_val}\n"
                                    f"  q = {q_bits[::-1]} -> {q_val}\n"
                                    f"  Verifikasi: {p_val} x {q_val} = {p_val * q_val}\n"
                                )


solve_binary_table(391)
