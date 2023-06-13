#include <stdio.h>
#include <stddef.h>
#include <string.h>
#include <sys/mman.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <errno.h>
#include <inttypes.h>

#define ALPHABET_SIZE 256

#define CLI_USAGE "\
USAGE:\n\
	exe <pattern> -- reads from pipe, not implemented\n\
	exe <pattern> <input file>\n\
	exe <pattern> -i <input text> -- not implemented\n\
"

static intptr_t table[ALPHABET_SIZE];
static char *pattern;
static char *input;
static size_t pattern_len;
static size_t input_len;

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

void compute_matches() {
	//size_t input_len = strlen(input);
	size_t align_end = pattern_len; // 1-based index of current alignment
	size_t i; // 1-based index of current input position
	size_t p; // 1-based index of current pattern position

	while (align_end <= input_len) {
		i = align_end;
		p = pattern_len;
		for (p = pattern_len; p >= 0;) {
			if (p == 0) {
				//found match at i..align_end inclusive
				printf("%d..%d\n", i + 1, align_end);
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
        fprintf(stderr, CLI_USAGE);
        return 1;
    }

	pattern = argv[1];
	pattern_len = strlen(pattern);
	if (pattern_len == 0) {
		fprintf(stderr, "ERROR: pattern cannot be empty");
        return 1;
	}

	int fd = open(argv[2], O_RDONLY);
	if (fd == -1) {
        fprintf(stderr, "Error opening file %s", argv[2]);
		perror("");
		return 1;
	}

    struct stat fd_stat;
    int fstat_return_val = fstat(fd, &fd_stat);
    if (fstat_return_val == -1) {
        perror("Error calling fstat on file descriptor");
        return 1;
    }
    input_len = fd_stat.st_size;

    input = mmap(NULL, input_len, PROT_READ, MAP_PRIVATE, fd, 0);
    if (input == MAP_FAILED) {
        perror("Error mapping input file into memory");
        return 1;
    }

	compute_table();
    printf("matches, inclusive 1-based sub lists\n");
	compute_matches();
}
