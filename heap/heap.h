#include<stdlib.h>
#include<stdio.h>

typedef struct {
    double distance;
    void * node;
} Node;


typedef struct {
    Node * nodes;
    int size;
    int limit;
} Heap;

Heap* construct_heap(const int limit);
void down(Heap * heap, const int index);
void up(Heap * heap, const int index);
void insert(Heap * heap, Node * node);
void free_heap(Heap * heap);