#include <stdio.h>
#include <stddef.h>
#include <string.h>
#include <sys/mman.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <errno.h>
#include <inttypes.h>
#include <fts.h>
#include <unistd.h>
#include <stdlib.h>

#define ALPHABET_SIZE 256

#define CLI_USAGE "\
USAGE:\n\
    exe <pattern> -- reads from pipe, not implemented\n\
    exe <pattern> <input file>...\n\
    exe <pattern> -i <input text> -- not implemented\n\
"

static intptr_t table[ALPHABET_SIZE];
static unsigned char *pattern;
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

void compute_matches(unsigned char *input, size_t input_len) {
    size_t align_end = pattern_len; // 1-based index of current alignment
    size_t i; // 1-based index of current input position
    size_t p; // 1-based index of current pattern position

    while (align_end <= input_len) {
        i = align_end;
        p = pattern_len;
        for (p = pattern_len; p >= 0;) {
            if (p == 0) {
                //found match at i
                printf("    %d\n", i);
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

int compare_dirs(const FTSENT **a, const FTSENT **b) {
    return strcmp( (**a).fts_name, (**b).fts_name );
}


int main(int argc, char *argv[]) {
    if (argc < 3) {
        fprintf(stderr, CLI_USAGE);
        return 1;
    }

    pattern = argv[1];
    pattern_len = strlen(pattern);
    if (pattern_len == 0) {
        fprintf(stderr, "ERROR: pattern cannot be empty");
        return 1;
    }

    compute_table();
    
    FTS *fts = fts_open(argv + 2, FTS_PHYSICAL, compare_dirs);
    FTSENT *ftsent;
    unsigned short fts_info;
    unsigned char *input;
    size_t input_len;
    int fd;

    while (ftsent = fts_read(fts)) {
        fts_info = ftsent->fts_info;

        if (fts_info == FTS_DNR ||
            fts_info == FTS_ERR ||
            fts_info == FTS_NS)
        {
            fprintf(stderr, "Error with fts_open %s: ", ftsent->fts_path);
            perror("");
            continue;
        }

        if (!S_ISREG(ftsent->fts_statp->st_mode)) {
            continue;
        }

        input_len = ftsent->fts_statp->st_size;

        // I shouldn't have to open an fd
        fd = open(ftsent->fts_path, O_RDONLY);
        if (fd == -1) {
            fprintf(stderr, "Error opening file descriptor for %s: ", ftsent->fts_path);
            perror("");
            exit(1);
        }

        input = mmap(NULL, input_len, PROT_READ, MAP_PRIVATE, fd, 0);
        if (input == MAP_FAILED) {
            fprintf(stderr, "Error mapping memory %s: ", ftsent->fts_path);
            perror("");
            return 1;
        }

        printf("%s\n", ftsent->fts_path);
        compute_matches(input, input_len);
        if (munmap(input, input_len) == -1) {
            fprintf(stderr, "Error unmapping memory %s: ", ftsent->fts_path);
            perror("");
            return 1;
        }

        if (close(fd) == -1) {
            fprintf(stderr, "Error closing file descriptor for %s\n", ftsent->fts_path);
            perror("");
            exit(1);
        }
    }
}
