#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <assert.h>
#include <stdlib.h>
#include <time.h>
#include "../allocator/allocator.h"
#include "../random_selection/random_selector.h"

struct node {
    struct node *next;
    uint8_t arr[16 - sizeof(struct node *)];
};
static_assert(sizeof(struct node) == 16, "cannot run experiment, size of node is not 16");

struct experiment {
    uint8_t *region;
    struct node *start;
    size_t num_nodes;
};

static struct experiment node_init(size_t num_nodes, size_t seed) {
    assert(num_nodes != 0);
    uint8_t *region = alloc(num_nodes * 16);
    struct node *node_arr = (struct node *) region;
    
    random_selector_setup(seed);
    selector_t s = random_selector_init(num_nodes);

    uint64_t idx = random_selector_pop(&s);
    struct node *start = &node_arr[idx];    
    struct node *prev = start;

    while (random_selector_is_empty(s) == false) {
        idx = random_selector_pop(&s);
        struct node *n = &node_arr[idx];

        prev->next = n;
        prev = n;
    }
    prev->next = start;

    random_selector_deinit(s);

    return (struct experiment) { 
        .region = region,
        .start = start,
        .num_nodes = num_nodes,
    };

}

static void node_deinit(struct experiment experiment) {
    alloc_free(experiment.region, experiment.num_nodes);
}

extern void benchmark(struct node *start, size_t steps);

int main(int argc, char *args[]) {
    if (argc != 4) {
        printf("Usage: %s <iterations> <len> <seed>\n", args[0]);
        exit(EXIT_FAILURE);
    }

    size_t iterations = atoll(args[1]);
    size_t len = atoll(args[2]);
    size_t seed = atoll(args[3]);

    for (size_t i = 0; i < iterations; ++i) {
        struct experiment exp = node_init(len, seed);

        struct timespec s, e;
        clock_gettime(CLOCK_MONOTONIC_RAW, &s);
        benchmark(exp.start, 100000000);
        clock_gettime(CLOCK_MONOTONIC_RAW, &e);

        uint64_t duration = 1e9 * (e.tv_sec - s.tv_sec) + (e.tv_nsec - s.tv_nsec);
        printf("%ld;%ld\n", len, duration);

        node_deinit(exp);
    }

}
