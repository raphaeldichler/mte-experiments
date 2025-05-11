#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <assert.h>
#include <stdlib.h>
#include <time.h>
#include <pthread.h>
#include "../allocator/allocator.h"
#include "../random_selection/random_selector.h"

pthread_barrier_t barrier;

struct node {
    struct node *next;
    uint8_t arr[16 - sizeof(struct node *)];
};

static_assert(sizeof(struct node) == 16, "cannot run experiment, size of node is not 16");

struct experiment {
    uint8_t *region;
    struct node *start1;
    struct node *start2;
    size_t num_nodes;
};

static struct experiment node_init(size_t num_nodes, size_t seed) {
    assert(num_nodes != 0);
    uint8_t *region = alloc(num_nodes * 16);
    struct node *node_arr = (struct node *) region;
    
    random_selector_setup(seed);
    selector_t s = random_selector_init(num_nodes);

    uint64_t idx = random_selector_pop(&s);
    struct node *start1 = &node_arr[idx];    
    struct node *prev = start1;

    num_nodes -= 2;
    size_t first_block = num_nodes / 2;
    for (size_t i = 0; i < first_block; ++i) {
        idx = random_selector_pop(&s);
        struct node *n = &node_arr[idx];

        prev->next = n;
        prev = n;
    }
    prev->next = start1;

  
    idx = random_selector_pop(&s);
    struct node *start2 = &node_arr[idx];    
    prev = start2;

    size_t second_block = num_nodes - first_block;
    for (size_t i = 0; i < second_block; ++i) {
        idx = random_selector_pop(&s);
        struct node *n = &node_arr[idx];

        prev->next = n;
        prev = n;
    }
    prev->next = start2;

    assert(random_selector_is_empty(s));
    random_selector_deinit(s);

    return (struct experiment) { 
        .region = region,
        .start1 = start1,
        .start2 = start2,
        .num_nodes = num_nodes,
    };
}

static void node_deinit(struct experiment experiment) {
    alloc_free(experiment.region, experiment.num_nodes);
}

#ifdef READ_ONLY
extern void benchmark(struct node *start, size_t steps);
#endif

#ifdef READ_WRITE
void benchmark(struct node *start, size_t steps, size_t write_on) {
    size_t wow = sizeof(struct node);
    for (size_t i = 0; i < steps; i++) {
        if (i % write_on == 0) {
            start->arr[1] += wow;
        }

        start = start->next;
    }
}
#endif

struct run_args {
  struct node *start;
  uint64_t duration;
};

static struct node *jump_forward(struct experiment *exp, size_t jumps) {

  
    struct node *start = NULL;
    if (jumps % 2 == 0) {
      start = exp->start1;
    } else {
      start = exp->start2;
    }

    for (size_t i = 0; i < jumps; ++i) {
      start = start->next;
    }
  
    return start;
}

static void *run(void *args) {
    struct run_args *a = (struct run_args *) args;
    pthread_barrier_wait(&barrier);
  
    struct timespec s, e;
    clock_gettime(CLOCK_MONOTONIC_RAW, &s);
#ifdef READ_ONLY
    benchmark(a->start, 100000000);
#endif

#ifdef READ_WRITE
    benchmark(a->start, 100000000, 1);
#endif

    clock_gettime(CLOCK_MONOTONIC_RAW, &e);



    a->duration = 1e9 * (e.tv_sec - s.tv_sec) + (e.tv_nsec - s.tv_nsec);

    return NULL;
}

#define MAX(x, y) (((x) > (y)) ? (x) : (y))

int main(int argc, char *args[]) {
    if (argc != 5) {
        printf("Usage: %s <iterations> <len> <seed> <threads>\n", args[0]);
        exit(EXIT_FAILURE);
    }

    size_t iterations = atoll(args[1]);
    size_t len = atoll(args[2]);
    size_t seed = atoll(args[3]);
    size_t num_threads = atoll(args[4]);
    size_t jumps[num_threads];
  
    for (size_t i = 0; i < num_threads; ++i) {
      jumps[i] = i + 1;
    }

    for (size_t i = 0; i < iterations; ++i) {
        struct experiment exp = node_init(len, seed);

        pthread_barrier_init(&barrier, NULL, num_threads);
        pthread_t threads[num_threads];
        struct run_args threads_args[num_threads];

        for (size_t j = 0; j < num_threads; ++j) {
          struct node *start = jump_forward(&exp, jumps[j]);
          assert(start != NULL);
          threads_args[j].start = start;
          pthread_create(&threads[j], NULL, run, &threads_args[j]);
        }
      
        for (size_t j = 0; j < num_threads; ++j) {
          pthread_join(threads[j], NULL);
        }

        uint64_t duration = 0;
        for (size_t j = 0; j < num_threads; ++j) {
          duration = MAX(threads_args[j].duration, duration);
        }
        printf("%ld;%ld;%ld\n", len, duration, num_threads);

        node_deinit(exp);
    }

}
