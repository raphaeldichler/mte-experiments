CC=gcc
CFLAGS=-O3
CFLAGS += -Wa,--noexecstack

default:
	make clean malloc malloc_mte
	bash benchmark.sh

malloc:
	$(CC) $(CFLAGS) -o malloc \
		-DALLOCATIONS=16777216 \
		main.c \
		../allocator/allocator.c

malloc_mte:
	$(CC) $(CFLAGS) -o malloc_mte \
		-DALLOCATIONS=16777216 \
		-DMTE -march=armv8.5-a+memtag \
		main.c \
		../allocator/tag_region.S \
		../allocator/allocator.c


clean:
	rm -rf results/ malloc malloc_mte
