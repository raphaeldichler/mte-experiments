CC=gcc
CFLAGS=-O3
CFLAGS += -Wa,--noexecstack

default:
	make clean write write_mte
	bash benchmark.sh

load_mte:
	$(CC) $(CFLAGS) -o load_mte \
		-DREAD_ONLY -DMTE -march=armv8.5-a+memtag \
		main.c \
		../random_selection/random_selector.c \
		../allocator/allocator.c \
		../allocator/tag_region.S \
		load.S 

load:
	$(CC) $(CFLAGS) -o load \
		-DREAD_ONLY \
		main.c \
		../random_selection/random_selector.c \
		../allocator/allocator.c \
		load.S 

write:
	$(CC) $(CFLAGS) -o write \
		-DREAD_WRITE \
		main.c \
		../random_selection/random_selector.c \
		../allocator/allocator.c

write_mte:
	$(CC) $(CFLAGS) -o write_mte \
		-DREAD_WRITE -DMTE -march=armv8.5-a+memtag \
		main.c \
		../random_selection/random_selector.c \
		../allocator/allocator.c \
		../allocator/tag_region.S

clean:
	rm -rf results/ *.png load load_mte write write_mte
