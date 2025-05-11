CC = gcc
CFLAGS = -O3
CFLAGS += -Wa,--noexecstack

default:
	make clean run run_mte
	bash benchmark.sh

run:
	$(CC) $(CFLAGS) -o run \
		main.c \
		../allocator/allocator.c \

run_mte:
	$(CC) $(CFLAGS) -o run_mte \
		-DMTE -march=armv8.5-a+memtag \
		main.c \
		../allocator/allocator.c  \
		../allocator/tag_region.S \

clean:
	rm -rf run run_mte results/ *.png
