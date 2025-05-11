CC=gcc
CFLAGS=-O3
CFLAGS += -Wa,--noexecstack

default:
	make clean load16 load16_mte
	bash benchmark.sh

load16:
	$(CC) $(CFLAGS) -o load16 \
		main.c \
		../allocator/allocator.c  \
		load.S

load16_mte:
	$(CC) $(CFLAGS) -o load16_mte \
		-DMTE -march=armv8.5-a+memtag \
		main.c \
		../allocator/allocator.c  \
		../allocator/tag_region.S \
		load.S

load16_mte_async:
	$(CC) $(CFLAGS) -o load16_mte_async \
		-DMTE -DASYNC -march=armv8.5-a+memtag \
		main.c \
		../allocator/allocator.c  \
		../allocator/tag_region.S \
		load.S

clean:
	rm -f load_mte_async load16 load16_mte
