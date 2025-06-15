run:
	gcc kdtree.c heap/heap.c heap/heap.h -o kdtree.out -lm && ./kdtree.out	

build_lib:
	gcc kdtree.c heap/heap.c heap/heap.h -o kdtree.out -lm && \
	./kdtree.out > /dev/null \
	gcc -c -fpic kdtree.c heap/heap.c heap/heap.h -lm && \
	gcc -shared -o libkdtree.so kdtree.o heap.o