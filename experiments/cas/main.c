#include <stdatomic.h>
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <assert.h>
#include <stdlib.h>
#include <sys/types.h>
#include <time.h>
#include <pthread.h>
#include <stdatomic.h>
#include "../allocator/allocator.h"

atomic_int *shared_var;    
pthread_barrier_t barrier;

#define NUM_ITERATION 100000000

static void* cas_benchmark(void* arg) {
    int expected;
    pthread_barrier_wait(&barrier);

    for (int i = 0; i < NUM_ITERATION; i++) {
        expected = atomic_load(shared_var);
        while (!atomic_compare_exchange_weak(shared_var, &expected, expected + 1)) {
            expected = atomic_load(shared_var);
        }
    }

    return NULL;
}


struct run_args {
  uint64_t duration;
};

static void *run(void *args) {
    struct run_args *a = (struct run_args *) args;
    pthread_barrier_wait(&barrier);

    struct timespec s, e;
    clock_gettime(CLOCK_MONOTONIC_RAW, &s);
    cas_benchmark(NULL);
    clock_gettime(CLOCK_MONOTONIC_RAW, &e);

    a->duration = 1e9 * (e.tv_sec - s.tv_sec) + (e.tv_nsec - s.tv_nsec);

    return NULL;
}


int main(int argc, char *args[]) {
    if (argc != 3) {
        printf("Usage: %s <iterations> <threads>\n", args[0]);
        exit(EXIT_FAILURE);
    }

    size_t iterations = atoll(args[1]);
    size_t num_threads = atoll(args[2]);

    for (size_t i = 0; i < iterations; ++i) {
        shared_var = alloc(16);
        *shared_var = 0;

        pthread_barrier_init(&barrier, NULL, num_threads);

        struct run_args threads_args[num_threads];
        pthread_t threads[num_threads];

        for (size_t j = 0; j < num_threads; ++j) {
          pthread_create(&threads[j], NULL, run, &threads_args[j]);
        }
      
        for (size_t j = 0; j < num_threads; ++j) {
          pthread_join(threads[j], NULL);
        }
        assert(*shared_var == num_threads * NUM_ITERATION);

        uint64_t duration = 0;
        for (size_t j = 0; j < num_threads; ++j) {
          duration += threads_args[j].duration;
        }

        printf("%ld;%ld\n", num_threads, duration);

        alloc_free(shared_var, 16);
    }

}
