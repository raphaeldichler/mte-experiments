CC=gcc
CFLAGS=-O3
CFLAGS += -Wa,--noexecstack

default:
	make clean tag_malloc tag_stg tag_st2g load store ldg
	bash benchmark.sh

tag_malloc:
	$(CC) $(CFLAGS) -o tag_malloc \
		-DMTE -DMALLOC -march=armv8.5-a+memtag \
		main.c \
		../allocator/tag_region.S 

tag_stg:
	$(CC) $(CFLAGS) -o tag_stg \
		-DMTE -DSTG -march=armv8.5-a+memtag \
		stg.S \
		main.c

tag_st2g:
	$(CC) $(CFLAGS) -o tag_st2g \
		-DMTE -DST2G -march=armv8.5-a+memtag \
		st2g.S \
		main.c

ldg:
	$(CC) $(CFLAGS) -o ldg \
		-DMTE -DLDG -march=armv8.5-a+memtag \
		../allocator/tag_region.S \
		ldg.S \
		main.c

load:
	$(CC) $(CFLAGS) -o load \
		-DLOAD \
		load.S \
		main.c 

store:
	$(CC) $(CFLAGS) -o store \
		-DSTORE \
		store.S \
		main.c 

clean:
	rm -rf results/ *.png tag_malloc tag_stg tag_st2g load store ldg
