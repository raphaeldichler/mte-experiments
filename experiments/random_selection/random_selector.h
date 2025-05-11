

#ifndef RANDOM_SELECTOR_H
#define RANDOM_SELECTOR_H

#include <stddef.h>
#include <stdint.h>

typedef struct selector {
    uint64_t *arr;
    size_t size;
} selector_t;


void random_selector_setup(size_t seed);

selector_t random_selector_init(size_t size);

void random_selector_deinit(selector_t s);

size_t random_selector_pop(selector_t *s);

bool random_selector_is_empty(selector_t s);


#endif // RANDOM_SELECTOR_H
