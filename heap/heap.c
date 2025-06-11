#include "heap.h"

int father(int index) {
    return (index - 1) / 2;
}

int left_child(int index) {
    return 2 * index + 1;
}

int right_child(int index) {
    return 2 * index + 2;
}

void swap(Node *x, Node *y) {
    Node temp = *x;
    *x = *y;
    *y = temp;
}

Heap* construct_heap(const int limit) {
    Heap* heap = (Heap*)malloc(sizeof(Heap));
    heap->nodes = (Node*)malloc(sizeof(Node) * limit);
    heap->size = 0;
    heap->limit = limit;
    return heap;
}

void down(Heap *heap, const int index) {
    int smallest = index;
    int left = left_child(index);
    int right = right_child(index);
    if (left < heap->size && heap->nodes[left].distance < heap->nodes[smallest].distance)
        smallest = left;
    if (right < heap->size && heap->nodes[right].distance < heap->nodes[smallest].distance)
        smallest = right;
    if (smallest == index) return;
    swap(&heap->nodes[index], &heap->nodes[smallest]);
    down(heap, smallest);
}

void up(Heap *heap, const int index) {
    if (index == 0) return;
    int parent = father(index);
    if (heap->nodes[index].distance >= heap->nodes[parent].distance) 
        return;    
    swap(&heap->nodes[index], &heap->nodes[parent]);
    up(heap, parent);
}

void insert(Heap *heap, Node *node) {
    if (heap->size >= heap->limit) return;
    heap->nodes[heap->size] = *node;
    up(heap, heap->size);
    heap->size++;
}

void free_heap(Heap *heap) {
    if (!heap) return;
    if (heap->nodes) free(heap->nodes);
    free(heap);
}