#include <stdio.h>
#include <stdint.h>
#include <stddef.h>
#include <string.h>
#include <stdlib.h>
#include <inttypes.h>
#include <stdatomic.h>

#include <omp.h>

#if defined(__x86_64__) || defined(__i386__)
#include <wmmintrin.h>
#include <cpuid.h>
#else
#error "This brute forcer requires x86/x86_64 with AES-NI support."
#endif

#include "generated_keyspace.h"


#ifndef FUTURE_RANK
#error "FUTURE_RANK is not defined. Did you generate generated_keyspace.h?"
#endif

#ifndef CIPHERTEXT_LEN
#error "CIPHERTEXT_LEN is not defined. Did you generate generated_keyspace.h?"
#endif


#if defined(__GNUC__)
#define AES_TARGET __attribute__((target("aes,sse2")))
#else
#define AES_TARGET
#endif


#define CHUNK_SIZE       (1ULL << 16)
#define PROGRESS_STEP    (1ULL << 24)


static atomic_int g_found = 0;
static atomic_uint_fast64_t g_next_chunk = 0;
static atomic_uint_fast64_t g_tested = 0;


static int cpu_has_aesni(void) {
    unsigned int eax, ebx, ecx, edx;

    if (!__get_cpuid(1, &eax, &ebx, &ecx, &edx)) {
        return 0;
    }

    return (ecx & bit_AES) != 0;
}


static void print_hex_key(const uint8_t key[16]) {
    for (int i = 0; i < 16; i++) {
        printf("%02x", key[i]);
    }
}


static void xor_delta_key(uint8_t key[16], unsigned int delta_idx) {
    for (int i = 0; i < 16; i++) {
        key[i] ^= DELTA_KEYS[delta_idx][i];
    }
}


static void make_key_from_mask(uint64_t mask, uint8_t key[16]) {
    memcpy(key, BASE_KEY, 16);

    for (unsigned int i = 0; i < FUTURE_RANK; i++) {
        if ((mask >> i) & 1ULL) {
            xor_delta_key(key, i);
        }
    }
}


static void advance_key_binary_increment(uint8_t key[16], uint64_t current_mask) {
    /*
     * Moving from current_mask to current_mask + 1:
     * all trailing 1 bits flip to 0, and the first 0 bit flips to 1.
     *
     * Therefore candidate key must xor DELTA_KEYS[0..t],
     * where t = number of trailing 1 bits in current_mask.
     */
    uint64_t inv = ~current_mask;
    unsigned int t = (unsigned int)__builtin_ctzll(inv);

    if (t >= FUTURE_RANK) {
        t = FUTURE_RANK - 1;
    }

    for (unsigned int i = 0; i <= t; i++) {
        xor_delta_key(key, i);
    }
}


AES_TARGET
static __m128i aes128_key_expansion_step(__m128i key, __m128i keygened) {
    keygened = _mm_shuffle_epi32(keygened, _MM_SHUFFLE(3, 3, 3, 3));

    __m128i tmp = _mm_slli_si128(key, 4);
    key = _mm_xor_si128(key, tmp);

    tmp = _mm_slli_si128(tmp, 4);
    key = _mm_xor_si128(key, tmp);

    tmp = _mm_slli_si128(tmp, 4);
    key = _mm_xor_si128(key, tmp);

    key = _mm_xor_si128(key, keygened);
    return key;
}


AES_TARGET
static void aes128_expand_decrypt_keys(const uint8_t raw_key[16], __m128i dec_keys[11]) {
    __m128i enc_keys[11];

    enc_keys[0] = _mm_loadu_si128((const __m128i *)raw_key);

    enc_keys[1]  = aes128_key_expansion_step(enc_keys[0],  _mm_aeskeygenassist_si128(enc_keys[0],  0x01));
    enc_keys[2]  = aes128_key_expansion_step(enc_keys[1],  _mm_aeskeygenassist_si128(enc_keys[1],  0x02));
    enc_keys[3]  = aes128_key_expansion_step(enc_keys[2],  _mm_aeskeygenassist_si128(enc_keys[2],  0x04));
    enc_keys[4]  = aes128_key_expansion_step(enc_keys[3],  _mm_aeskeygenassist_si128(enc_keys[3],  0x08));
    enc_keys[5]  = aes128_key_expansion_step(enc_keys[4],  _mm_aeskeygenassist_si128(enc_keys[4],  0x10));
    enc_keys[6]  = aes128_key_expansion_step(enc_keys[5],  _mm_aeskeygenassist_si128(enc_keys[5],  0x20));
    enc_keys[7]  = aes128_key_expansion_step(enc_keys[6],  _mm_aeskeygenassist_si128(enc_keys[6],  0x40));
    enc_keys[8]  = aes128_key_expansion_step(enc_keys[7],  _mm_aeskeygenassist_si128(enc_keys[7],  0x80));
    enc_keys[9]  = aes128_key_expansion_step(enc_keys[8],  _mm_aeskeygenassist_si128(enc_keys[8],  0x1B));
    enc_keys[10] = aes128_key_expansion_step(enc_keys[9],  _mm_aeskeygenassist_si128(enc_keys[9],  0x36));

    dec_keys[0] = enc_keys[10];

    for (int i = 1; i < 10; i++) {
        dec_keys[i] = _mm_aesimc_si128(enc_keys[10 - i]);
    }

    dec_keys[10] = enc_keys[0];
}


AES_TARGET
static void aes128_decrypt_block(
    const uint8_t in[16],
    uint8_t out[16],
    const __m128i dec_keys[11]
) {
    __m128i block = _mm_loadu_si128((const __m128i *)in);

    block = _mm_xor_si128(block, dec_keys[0]);

    for (int round = 1; round < 10; round++) {
        block = _mm_aesdec_si128(block, dec_keys[round]);
    }

    block = _mm_aesdeclast_si128(block, dec_keys[10]);

    _mm_storeu_si128((__m128i *)out, block);
}


static int pkcs7_padding_valid(const uint8_t *plain, size_t len) {
    if (len == 0 || (len % 16) != 0) {
        return 0;
    }

    uint8_t pad = plain[len - 1];

    if (pad == 0 || pad > 16 || pad > len) {
        return 0;
    }

    for (size_t i = 0; i < pad; i++) {
        if (plain[len - 1 - i] != pad) {
            return 0;
        }
    }

    return 1;
}


static int last_block_padding_maybe_valid(const uint8_t last_block[16]) {
    uint8_t pad = last_block[15];

    if (pad == 0 || pad > 16) {
        return 0;
    }

    for (uint8_t i = 0; i < pad; i++) {
        if (last_block[15 - i] != pad) {
            return 0;
        }
    }

    return 1;
}


static int is_printable_ascii_message(const uint8_t *plain, size_t len) {
    for (size_t i = 0; i < len; i++) {
        uint8_t c = plain[i];

        if (
            (c >= 0x20 && c <= 0x7e) ||
            c == '\n' ||
            c == '\r' ||
            c == '\t'
        ) {
            continue;
        }

        return 0;
    }

    return 1;
}


static int contains_flag_pattern(const uint8_t *plain, size_t len) {
    const char needle[] = "SCTF26{";
    const size_t needle_len = sizeof(needle) - 1;

    if (len < needle_len + 1) {
        return 0;
    }

    for (size_t i = 0; i + needle_len <= len; i++) {
        if (memcmp(plain + i, needle, needle_len) == 0) {
            for (size_t j = i + needle_len; j < len; j++) {
                if (plain[j] == '}') {
                    return 1;
                }
            }
        }
    }

    return 0;
}


static int try_candidate_key(
    const uint8_t key[16],
    uint8_t plaintext_out[CIPHERTEXT_LEN]
) {
    __m128i dec_keys[11];

    aes128_expand_decrypt_keys(key, dec_keys);

    /*
     * Optimization:
     * Decrypt the last block first. Most wrong keys fail PKCS#7 padding.
     */
    uint8_t last_block[16];
    aes128_decrypt_block(
        CIPHERTEXT + CIPHERTEXT_LEN - 16,
        last_block,
        dec_keys
    );

    if (!last_block_padding_maybe_valid(last_block)) {
        return 0;
    }

    for (size_t off = 0; off < CIPHERTEXT_LEN; off += 16) {
        if (off == CIPHERTEXT_LEN - 16) {
            memcpy(plaintext_out + off, last_block, 16);
        } else {
            aes128_decrypt_block(
                CIPHERTEXT + off,
                plaintext_out + off,
                dec_keys
            );
        }
    }

    if (!pkcs7_padding_valid(plaintext_out, CIPHERTEXT_LEN)) {
        return 0;
    }

    uint8_t pad = plaintext_out[CIPHERTEXT_LEN - 1];
    size_t msg_len = CIPHERTEXT_LEN - pad;

    if (!is_printable_ascii_message(plaintext_out, msg_len)) {
        return 0;
    }

    if (!contains_flag_pattern(plaintext_out, msg_len)) {
        return 0;
    }

    return 1;
}


static uint64_t total_candidates(void) {
    if (FUTURE_RANK == 0) {
        return 1ULL;
    }

    if (FUTURE_RANK >= 63) {
        fprintf(
            stderr,
            "[-] FUTURE_RANK=%d is too large for this uint64_t enumerator.\n",
            FUTURE_RANK
        );
        exit(1);
    }

    return 1ULL << FUTURE_RANK;
}


int main(void) {
    if (!cpu_has_aesni()) {
        fprintf(stderr, "[-] AES-NI is not available on this CPU.\n");
        fprintf(stderr, "[-] Run this on an x86_64 CPU with AES instruction support.\n");
        return 1;
    }

    const uint64_t total = total_candidates();

    printf("[+] FUTURE_RANK    : %d\n", FUTURE_RANK);
    printf("[+] candidates     : 2^%d = %" PRIu64 "\n", FUTURE_RANK, total);
    printf("[+] ciphertext len : %d\n", CIPHERTEXT_LEN);
    printf("[+] OpenMP threads : %d\n", omp_get_max_threads());
    fflush(stdout);

    #pragma omp parallel
    {
        uint8_t key[16];
        uint8_t plaintext[CIPHERTEXT_LEN];

        while (!atomic_load_explicit(&g_found, memory_order_relaxed)) {
            uint64_t start = atomic_fetch_add_explicit(
                &g_next_chunk,
                CHUNK_SIZE,
                memory_order_relaxed
            );

            if (start >= total) {
                break;
            }

            uint64_t end = start + CHUNK_SIZE;
            if (end < start || end > total) {
                end = total;
            }

            make_key_from_mask(start, key);

            for (uint64_t mask = start; mask < end; mask++) {
                if (atomic_load_explicit(&g_found, memory_order_relaxed)) {
                    break;
                }

                if (try_candidate_key(key, plaintext)) {
                    int expected = 0;

                    if (atomic_compare_exchange_strong(&g_found, &expected, 1)) {
                        uint8_t pad = plaintext[CIPHERTEXT_LEN - 1];
                        size_t msg_len = CIPHERTEXT_LEN - pad;

                        #pragma omp critical(found_print)
                        {
                            printf("\n[+] FOUND!\n");
                            printf("[+] mask      : 0x%016" PRIx64 "\n", mask);
                            printf("[+] key hex   : ");
                            print_hex_key(key);
                            printf("\n");
                            printf("[+] plaintext :\n");
                            printf("%.*s\n", (int)msg_len, plaintext);
                            fflush(stdout);
                        }
                    }

                    break;
                }

                if (mask + 1 < end) {
                    advance_key_binary_increment(key, mask);
                }
            }

            uint64_t done = atomic_fetch_add_explicit(
                &g_tested,
                end - start,
                memory_order_relaxed
            ) + (end - start);

            if (
                done / PROGRESS_STEP !=
                (done - (end - start)) / PROGRESS_STEP
            ) {
                #pragma omp critical(progress_print)
                {
                    double pct = 100.0 * (double)done / (double)total;
                    fprintf(
                        stderr,
                        "[+] progress: %.4f%% (%" PRIu64 "/%" PRIu64 ")\n",
                        pct,
                        done,
                        total
                    );
                    fflush(stderr);
                }
            }
        }
    }

    if (!atomic_load_explicit(&g_found, memory_order_relaxed)) {
        printf("[-] no valid key/plaintext found in generated keyspace\n");
        return 2;
    }

    return 0;
}
