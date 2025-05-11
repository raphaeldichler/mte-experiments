#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <assert.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <sys/types.h>
#include <unistd.h>
#include <sys/auxv.h>
#include <sys/mman.h>
#include <sys/prctl.h>
#include <time.h>
#include "../allocator/allocator.h"

#define _GNU_SOURCE

#include <stdio.h>
#include <stdlib.h>
#include <sys/prctl.h>

#define PR_TAGGED_ADDR_ENABLE (1UL << 0)

#define WARUM_UP 1

struct bench {
    size_t allocation;
    size_t bytes_to_alloc;
    void *ptrs[ALLOCATIONS];
};

void benchmark(struct bench *bench) {
    for (size_t i = 0; i < bench->allocation; ++i) {
        bench->ptrs[i] = malloc(bench->bytes_to_alloc);
    }
}

int main(int argc, char *args[]) {
    if (argc != 3) {
        printf("Usage: %s <iterations> <size>\n", args[0]);
        exit(EXIT_FAILURE);
    }

    size_t iterations = atoll(args[1]);
    size_t size = atoll(args[2]);

    size_t allocations = (1 << 28) / size;
    // ensure we size is a multiple of 16, to match granularity
    assert(size % 16 == 0);
    assert(allocations * size < (1 << 29));

    void *ptr = malloc(1024);

    struct bench *bench= alloc(sizeof(struct bench));
    bench->allocation = allocations;
    bench->bytes_to_alloc = size;
    for (size_t i = 0; i < iterations + WARUM_UP; ++i) {

        struct timespec s, e1, e2;
        clock_gettime(CLOCK_MONOTONIC_RAW, &s);
        benchmark(bench);
        clock_gettime(CLOCK_MONOTONIC_RAW, &e1);

        for (size_t j = 0; j < bench->allocation; ++j) {
            free(bench->ptrs[j]);
        }

        clock_gettime(CLOCK_MONOTONIC_RAW, &e2);

        if (i > WARUM_UP) {
            uint64_t duration_allocation = 1e9 * (e1.tv_sec - s.tv_sec) + (e1.tv_nsec - s.tv_nsec);
            uint64_t duration_deallocation = 1e9 * (e2.tv_sec - e1.tv_sec) + (e2.tv_nsec - e1.tv_nsec);

            printf("%ld;%ld;%ld;%ld\n", size, allocations, duration_allocation, duration_deallocation);
        }

    }

    alloc_free(bench, sizeof(struct bench));
    free(ptr);
}
