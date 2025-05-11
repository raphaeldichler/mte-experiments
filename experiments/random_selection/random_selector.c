#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <assert.h>
#include <stdbool.h>

#include "random_selector.h"


void random_selector_setup(size_t seed) {
    srand(seed);
}

selector_t random_selector_init(size_t size) {
    assert(size < UINT64_MAX);

    uint64_t *arr = malloc(sizeof(*arr) * size);
    if (!arr) {
        perror("OOM - failed to init selector");
        exit(EXIT_FAILURE);
    }

    for (size_t i = 0; i < size; ++i) {
        arr[i] = i;
    }

    return (selector_t) {
        .arr = arr,
        .size = size,
    };
}

void random_selector_deinit(selector_t s) {
    free(s.arr);
}

uint64_t random_selector_pop(selector_t *s) {
    assert(s->size != 0);

    uint32_t next = rand() % s->size;
    s->size -= 1;
    
    uint64_t element = s->arr[next];
    assert(element != UINT64_MAX);
    
    s->arr[next] = s->arr[s->size];
    s->arr[s->size] = UINT64_MAX;

    return element;
}


bool random_selector_is_empty(selector_t s) {
    return  s.size == 0;
}
