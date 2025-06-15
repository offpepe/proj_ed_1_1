from ctypes import Structure, POINTER, c_double, c_int,c_char, c_float, c_void_p, CFUNCTYPE, CDLL


#region DEF KDTREE
class TReg(Structure):
    _fields_ = [("embed", c_float *128), 
                ("nome",c_char *100)
                ]

class TNode(Structure):
    pass

TNode._fields_ = [("key", c_void_p),
                  ("esq", POINTER(TNode)),
                  ("dir", POINTER(TNode))]

class Tarv(Structure):
    _fields_ = [("k", c_int),
                ("dist", CFUNCTYPE(c_double, c_void_p, c_void_p)),
                ("cmp", CFUNCTYPE(c_int, c_void_p, c_void_p, c_int)),
                ("raiz", POINTER(TNode))]
#endregion

#region DEF HEAP
class Node(Structure):
    _fields_ = [("distance", c_double),
                ("node", c_void_p)]

class Heap(Structure):
    _fields_ = [("nodes", POINTER(Node)),
                ("size", c_int),
                ("limit", c_int)]
#endregion

lib = CDLL("./libkdtree.so")
#region heap
lib.construct_heap.argtypes = [c_int]
lib.construct_heap.restype = POINTER(Heap)
lib.down.argtypes = [POINTER(Heap), c_int]
lib.down.restype = None
lib.up.argtypes = [POINTER(Heap), c_int]
lib.up.restype = None
lib.insert.argtypes = [POINTER(Heap), POINTER(Node)]
lib.insert.restype = None
lib.free_heap.argtypes = [POINTER(Heap)]
lib.free_heap.restype = None
#endregion
#region kdtree
lib.buscar_mais_proximo.argtypes = [POINTER(Tarv), TReg]
lib.buscar_mais_proximo.restype = TReg
lib.get_tree.restype = POINTER(Tarv)
lib.inserir_ponto.argtypes = [TReg]
lib.inserir_ponto.restype = None
lib.kdtree_construir.argtypes = []
lib.kdtree_construir.restype = None
#endregion