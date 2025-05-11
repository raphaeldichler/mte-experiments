#include <stddef.h>
#include <assert.h>
#include <stdlib.h>
#include <stdio.h>
#include <sys/mman.h>
#include <stdint.h>

#include <sys/auxv.h>
#include <sys/prctl.h>
#include <time.h>

#ifdef MTE
#include <arm_acle.h>
#endif

#define insert_random_tag(ptr) ({                       \
        uint64_t __val;                                 \
        asm("irg %0, %1" : "=r" (__val) : "r" (ptr));   \
        __val;                                          \
})

#ifdef ASYNC
#define MTE_MODE PR_MTE_TCF_ASYNC
#else 
#define MTE_MODE PR_MTE_TCF_SYNC
#endif

#define set_tag(tagged_addr) do {                                      \
        asm volatile("stg %0, [%0]" : : "r" (tagged_addr) : "memory"); \
} while (0)


#define set_tag32(tagged_addr) do {                                      \
        asm volatile("st2g %0, [%0]" : : "r" (tagged_addr) : "memory"); \
} while (0)

#ifdef MALLOC
extern void *mtag_tag_region(void *ptr, size_t size);
#endif

#ifdef STG 
extern void benchmark_stg(uint8_t *ptr, size_t len);
#endif

#ifdef ST2G 
void benchmark_st2g(uint8_t *ptr, size_t len);
#endif

#ifdef LOAD
extern void benchmark_load(uint32_t *arr, size_t len);
#endif

#ifdef STORE
extern void benchmark_store(uint32_t *arr, size_t len, size_t add);
#endif

#ifdef LDG
extern void benchmark_ldg(uint8_t *ptr, size_t len);
extern void *mtag_tag_region(void *ptr, size_t size);
#endif

#ifdef IRG
extern void benchmark_irg(uint8_t *ptr, size_t len);
#endif


void benchmark(size_t bytes) {
#ifdef MTE
  void *mem = mmap(NULL, bytes, PROT_READ | PROT_WRITE | PROT_MTE, MAP_ANONYMOUS | MAP_PRIVATE, -1, 0);
#else
  void *mem = mmap(NULL, bytes, PROT_READ | PROT_WRITE, MAP_ANONYMOUS | MAP_PRIVATE, -1, 0);
#endif
  uint8_t *pp = mem;
  for (size_t i = 0; i < bytes; i += 1024) {
      pp[i]++;
  }
#ifdef LDG
  void *p = __arm_mte_create_random_tag(mem, 0);
  mem = mtag_tag_region(mem, bytes);
#endif

  size_t bytes_processed = 0;
  size_t ops = 0;

  struct timespec s, e;
  clock_gettime(CLOCK_MONOTONIC_RAW, &s);
#ifdef MALLOC
  void *p = __arm_mte_create_random_tag(mem, 0);
  mem = mtag_tag_region(mem, bytes);
  ops = bytes / 32;
  bytes_processed = bytes / 16;
#endif

#ifdef STG
  benchmark_stg(mem, bytes);
  ops = bytes / 16;
  bytes_processed = bytes / 16;
#endif

#ifdef ST2G
  benchmark_st2g(mem, bytes);
  ops = bytes / 32;
  bytes_processed = bytes / 16;
#endif

#ifdef LOAD
  benchmark_load((uint32_t *) pp, bytes / 4);
  ops = bytes / 4;
  bytes_processed = bytes;
#endif
  
#ifdef STORE
  benchmark_store((uint32_t *) pp, bytes / 4, 37);
  ops = bytes / 4;
  bytes_processed = bytes;
#endif

#ifdef LDG
  benchmark_ldg(mem, bytes);
  ops = bytes / 16;
  bytes_processed = bytes / 16;
#endif

#ifdef IRG
  benchmark_irg(mem, bytes);
  ops = bytes / 4;
  bytes_processed = bytes;
#endif

  clock_gettime(CLOCK_MONOTONIC_RAW, &e);

  assert(bytes_processed > 0);
  assert(ops > 0);
  uint64_t duration = 1e9 * (e.tv_sec - s.tv_sec) + (e.tv_nsec - s.tv_nsec);
  printf("%ld;%ld;%ld;%ld\n", bytes, duration, ops, bytes_processed);

  if (munmap(mem, bytes) == -1) {
    perror("mmap");
    exit(EXIT_FAILURE);
  }
}


int main(int argc, char *args[]) {
    if (argc != 3) {
        printf("Usage: %s <iterations> <size>\n", args[0]);
        exit(EXIT_FAILURE);
    }

#ifdef MTE
    unsigned long hwcap2 = getauxval(AT_HWCAP2);

    /* check if MTE is present */
    if (!(hwcap2 & HWCAP2_MTE)) {
      perror("MTE is not present");
      exit(EXIT_FAILURE);
    }

    /*
     * Enable MTE with synchronous checking
     */
    if (prctl(PR_SET_TAGGED_ADDR_CTRL,
          PR_TAGGED_ADDR_ENABLE | MTE_MODE | (0xfffe << PR_MTE_TAG_SHIFT),
          0, 0, 0)) {
      perror("prctl() failed");
      exit(EXIT_FAILURE);
    }
#endif

    size_t iterations = atoll(args[1]);
    size_t size = atoll(args[2]);

    for (size_t i = 0; i < iterations; ++i) {
      benchmark(size);
    }
}
