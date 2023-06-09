#include <stdio.h>
#include <stddef.h>
#include <string.h>

#define ALPHABET_SIZE 256

static size_t table[ALPHABET_SIZE];
static char *pattern;
static size_t pattern_len;

size_t max(size_t a, size_t b) {
	return a>b ? a : b;
}

void compute_table() {	
	for (size_t i = 0; i < ALPHABET_SIZE; i++) {
		table[i] = pattern_len;
	}

	size_t shiftby = pattern_len - 1;
	for (size_t i = 0; i < pattern_len - 1; i++) {
		table[pattern[i]] = shiftby--;
	}
}

void compute_matches(char *input) {
	size_t input_len = strlen(input);
	size_t align_end = pattern_len; // 1-based index of current alignment
	size_t i; // 1-based index of current input position
	size_t p; // 1-based index of current pattern position

	while (align_end <= input_len) {
		i = align_end;
		p = pattern_len;
		for (p = pattern_len; p >= 0;) {
			if (p == 0) {
				//found match at i..align_end inclusive
				printf("%d..%d inclusive, 1-based indexing\n", i, align_end - 1);
				align_end++;
				break;
			}
			// switch to 0-based indexing
			p--;
			i--;

			if (pattern[p] != input[i]) {
				align_end = max(align_end + 1, i + table[input[i]]);
				break;
			}
		}
	}
}

int main(int argc, char *argv[]) {

	if (argc != 3) {
		fprintf(stderr, "found %d arguments\n", argc);
		fprintf(stderr, "usage: exe <pattern> <input>\n");
		return 1;
	}

	pattern = argv[1];
	pattern_len = strlen(pattern);

	compute_table();
	compute_matches(argv[2]);

}
