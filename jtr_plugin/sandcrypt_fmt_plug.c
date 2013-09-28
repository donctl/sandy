/*
 * =====================================================================================
 *
 *       Filename:  sandcrypt_fmt_plug.c
 *
 *    Description:  Implements a bruteforcer to the samsung way of android disk
 *                  encryption. It is part of the sandy framework, thus the same license
 *                  applies.
 *
 *        Version:  0.1
 *        Created:  09/24/2013 15:49:10
 *       Revision:  none
 *       Compiler:  gcc
 *
 *         Author:  Laszlo Toth 
 *   Organization:  
 *
 * =====================================================================================
 */

#include <openssl/opensslv.h>
#include <openssl/evp.h>
#include <openssl/HMAC.h>
#if OPENSSL_VERSION_NUMBER >= 0x00908000

#include <string.h>

#include "arch.h"
#include "misc.h"
#include "common.h"
#include "formats.h"
#include <openssl/sha.h>

#define FORMAT_LABEL			"sandcrypt"
#define FORMAT_NAME			"Samsung phone encryption"

#define ALGORITHM_NAME			"32/" ARCH_BITS_STR

#define BENCHMARK_COMMENT		""
#define BENCHMARK_LENGTH		0

#define PLAINTEXT_LENGTH		125

#define BINARY_SIZE			32
#define SALT_SIZE			48
#define SALT_SIZE_REAL			16
#define ENC_KEY_SIZE			32
#define CIPHERTEXT_LENGTH		(ENC_KEY_SIZE * 2 + BINARY_SIZE * 2 + SALT_SIZE_REAL*2)

#define MIN_KEYS_PER_CRYPT		1
#define MAX_KEYS_PER_CRYPT		1

static struct fmt_tests tests[] = {
	{"37257bc9136d9da22756780fc8e6f5675a040adccbe92048e985e21a82f043a08172ee2f0f06cc7c3c8e0faad4bbaa3ff15a94f74c1cd5962ff496096bc6d8dea0a014b7b81c655baf725fb94cb2aada", "qwerty1"},
	{NULL}
};

static char crypt_key[BINARY_SIZE+1];
static unsigned char cursalt[SALT_SIZE_REAL];
static unsigned char curenckey[BINARY_SIZE];
static char saved_plain[PLAINTEXT_LENGTH + 1];

static int valid(char *ciphertext, struct fmt_main *self)
{
	int i;

	if (strlen(ciphertext) != CIPHERTEXT_LENGTH) return 0;
	for (i = 0; i < CIPHERTEXT_LENGTH; i++)
	{
		if (!(  (('0' <= ciphertext[i])&&(ciphertext[i] <= '9')) ||
		        (('a' <= ciphertext[i])&&(ciphertext[i] <= 'f'))
		        || (('A' <= ciphertext[i])&&(ciphertext[i] <= 'F'))))
			return 0;
	}
	return 1;
}


static char *split(char *ciphertext, int index)
{
	static char out[CIPHERTEXT_LENGTH + 1];

	strnzcpy(out, ciphertext, CIPHERTEXT_LENGTH + 1);
	strlwr(out);

	return out;
}

static void set_salt(void *salt)
{
	memcpy(curenckey, salt, BINARY_SIZE);
	memcpy(cursalt, salt+BINARY_SIZE, SALT_SIZE_REAL);
}

static void set_key(char *key, int index)
{
	int len;
	int i;
	len = strlen(key);
	memcpy(saved_plain, key, len);
	saved_plain[len] = 0;
}

static char *get_key(int index)
{
	return saved_plain;
}

static int cmp_all(void *binary, int count)
{
	return !memcmp(binary, crypt_key, BINARY_SIZE);
}

static int cmp_exact(char *source, int count)
{
	return (1);
}

static int cmp_one(void *binary, int index)
{
	return !memcmp(binary, crypt_key, BINARY_SIZE);
}

static void crypt_all(int count)
{
	static unsigned char key[64];
	unsigned char fixed_hex_1[17]="\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f";
	unsigned char fixed_hex_2[17]="\x01\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f";
	int i;
	int out_len;
	
	out_len=32;
	PKCS5_PBKDF2_HMAC(saved_plain, strlen(saved_plain), cursalt, 16, 4096, EVP_sha256(), 32, key);
	HMAC(EVP_sha256(), key, 32, curenckey, 32, crypt_key, NULL);
}

static void *binary(char *ciphertext)
{
	static unsigned char realcipher[BINARY_SIZE];
	int i;

	for(i=0;i<BINARY_SIZE;i++)
		realcipher[i] = atoi16[ARCH_INDEX(ciphertext[i*2+64])]*16 + atoi16[ARCH_INDEX(ciphertext[i*2+1+64])];

	return (void*)realcipher;
}

static void *salt(char *ciphertext)
{
	static unsigned char salt[BINARY_SIZE+SALT_SIZE_REAL];
	int i;

	memset(salt, 0, sizeof(salt));
	for(i=0;i<BINARY_SIZE;i++)
		salt[i] = atoi16[ARCH_INDEX(ciphertext[i*2])]*16 + atoi16[ARCH_INDEX(ciphertext[i*2+1])];
	for(i=32;i<SALT_SIZE_REAL+32;i++)
		salt[i] = atoi16[ARCH_INDEX(ciphertext[i*2+64])]*16 + atoi16[ARCH_INDEX(ciphertext[i*2+1+64])];
	return salt;
}

void print_hex(unsigned char* d, int len){
	int i;
	
	for(i=0; i < len; i++){
		printf("%02x", d[i]);
	}
}

struct fmt_main fmt_sandcrypt = {
	{
		FORMAT_LABEL,
		FORMAT_NAME,
		ALGORITHM_NAME,
		BENCHMARK_COMMENT,
		BENCHMARK_LENGTH,
		PLAINTEXT_LENGTH,
		BINARY_SIZE,
		SALT_SIZE,
		MIN_KEYS_PER_CRYPT,
		MAX_KEYS_PER_CRYPT,
		FMT_CASE | FMT_8_BIT | FMT_SPLIT_UNIFIES_CASE,
		tests
	}, {
		fmt_default_init,
		fmt_default_prepare,
		valid,
		split,
		binary,
		salt,
		{
			fmt_default_binary_hash,
			fmt_default_binary_hash,
			fmt_default_binary_hash,
			fmt_default_binary_hash,
			fmt_default_binary_hash
		},
		fmt_default_salt_hash,
		set_salt,
		set_key,
		get_key,
		fmt_default_clear_keys,
		crypt_all,
		{
			fmt_default_get_hash,
			fmt_default_get_hash,
			fmt_default_get_hash,
			fmt_default_get_hash,
			fmt_default_get_hash
		},
		cmp_all,
		cmp_one,
		cmp_exact
	}
};

#else
#ifdef __GNUC__
#warning Note: sandcrypt format disabled - it needs OpenSSL 0.9.8 or above
#endif

#endif
