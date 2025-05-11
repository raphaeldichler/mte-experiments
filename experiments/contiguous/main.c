#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <assert.h>
#include <stdlib.h>
#include <time.h>
#include "../allocator/allocator.h"

struct node {
    uint64_t val;
    uint8_t arr[16 - sizeof(uint64_t)];
};
static_assert(sizeof(struct node) == 16, "cannot run experiment, size of node is not 16");

extern void benchmark(uint32_t *ptr, size_t len);

#define WARUM_UP 5

int main(int argc, char *args[]) {
    if (argc != 4) {
        printf("Usage: %s <iterations> <len> <runs>\n", args[0]);
        exit(EXIT_FAILURE);
    }

    size_t iterations = atoll(args[1]);
    size_t len = atoll(args[2]);
    size_t runs = atoll(args[3]);

    // we only test with lengths of power of 2 - this is done to simplify the benchmark
    assert((len & (len - 1)) == 0);

    for (size_t i = 0; i < iterations + WARUM_UP; ++i) {
        size_t num_bytes = len * 64;
        uint8_t *region = alloc(num_bytes);

        struct timespec s, e;
        clock_gettime(CLOCK_MONOTONIC_RAW, &s);
        benchmark((uint32_t *)region, num_bytes / 4); 
        clock_gettime(CLOCK_MONOTONIC_RAW, &e);
        
        if (i > WARUM_UP) {
          uint64_t duration = 1e9 * (e.tv_sec - s.tv_sec) + (e.tv_nsec - s.tv_nsec);
          printf("%ld;%ld;%ld\n", len, duration, runs);
        }

        alloc_free(region, num_bytes);
    }

}
