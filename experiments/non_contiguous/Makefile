CC=gcc
CFLAGS=-O3
CFLAGS += -Wa,--noexecstack

default:
	make clean load load_mte load_mte_async
	bash benchmark.sh

load_mte:
	$(CC) $(CFLAGS) -o load_mte \
		-DMTE -march=armv8.5-a+memtag \
		main.c \
		../random_selection/random_selector.c \
		../allocator/allocator.c \
		../allocator/tag_region.S \
		load.S 

load_mte_async:
	$(CC) $(CFLAGS) -o load_mte_async \
		-DMTE -DASYNC -march=armv8.5-a+memtag \
		main.c \
		../random_selection/random_selector.c \
		../allocator/allocator.c \
		../allocator/tag_region.S \
		load.S 

load:
	$(CC) $(CFLAGS) -o load \
		main.c \
		../random_selection/random_selector.c \
		../allocator/allocator.c \
		load.S 

clean:
	rm -rf load load_mte load_mte_async
