# app.py

import os
from fastapi import FastAPI, Query, UploadFile, Form, HTTPException
from kdtree_wrapper import lib, Tarv, TReg
from ctypes import POINTER, c_char, c_float
from pydantic import BaseModel
from deepface import DeepFace
from PIL import Image
from io import BytesIO
from numpy import array, dtype, zeros, ndarray
from concurrent.futures import ThreadPoolExecutor
import concurrent.futures

DATASET_PATH = './dataset'
MAX_CONCURRENCY_LEVEL = 8
app = FastAPI()


class PontoEntrada(BaseModel):
    file: UploadFile
    nome: str
    
class QueryInput(BaseModel):
    embbed: list[float]
    
C_FLOAT_ARRAY_128 = c_float * 128

def list_to_c_float_array(float_list: list[float]) -> C_FLOAT_ARRAY_128: # type: ignore
    return C_FLOAT_ARRAY_128(*float_list[:128])

def get_face_embbed(file: bytes, name: str = "complete_unknown") -> list[C_FLOAT_ARRAY_128]: # type: ignore
    image = Image.open(file)
    faces = DeepFace.extract_faces(array(image))
    embbeds : list = []
    for face in faces:
        FA = face['facial_area']
        croppedFace = image.crop((FA['x'], 
                       FA['y'],
                       FA['x'] + FA['w'], 
                       FA['y'] + FA['h']))
        representation = DeepFace.represent(array(croppedFace), 'Facenet')
        if (not len(representation)):
            print(f"couldn't represate image of {name} as embbed")
            continue
        embbeds.append(C_FLOAT_ARRAY_128(
            *representation[0]['embedding'][:128]
            ))
    return embbeds


def process_file(directorie, file):
    file_path = os.path.join(DATASET_PATH, directorie, file)
    print(f"[{file_path}] Starting process")
    try:
        with open(file_path, 'rb') as fileBytes:
            print(f"[{file_path}] converting to embbed")
            embbeds = get_face_embbed(BytesIO(fileBytes.read()))
            points = []
            for embbed in embbeds:
                ponto = TReg(embed=embbed, nome=directorie.encode('utf-8')[:99])
                points.append(ponto)
            print(f"[{file_path}] image converted")
            return points, os.path.join(directorie, file)
    except:
        return [], None

def load_dataset():
    inserted_embbeds = []
    tasks = []
    for directorie in os.listdir(DATASET_PATH):
        files = os.listdir(os.path.join(DATASET_PATH, directorie))
        for file in files:
            tasks.append((directorie, file))
    
    with ThreadPoolExecutor(max_workers=MAX_CONCURRENCY_LEVEL) as executor:
        future_to_task = {executor.submit(process_file, directorie, file): (directorie, file) 
                         for directorie, file in tasks}
        
        for future in concurrent.futures.as_completed(future_to_task):
            points, file_path = future.result()
            if file_path:
                for ponto in points:
                    lib.inserir_ponto(ponto)
                inserted_embbeds.append(file_path)
    
    return inserted_embbeds
                                   

@app.post("/construir-arvore")
async def constroi_arvore():
    lib.kdtree_construir()
    inserted_embbeds = load_dataset()
    return {
        "mensagem": "Árvore KD inicializada com sucesso.",
        "total_inseridos": len(inserted_embbeds), 
        "inseridos": inserted_embbeds}

@app.post("/inserir")
async def inserir(nome: str = Form(...), file: UploadFile = UploadFile(...)):
    if (not file.size):
        raise HTTPException(status_code=400, detail="É necessário incluir um arquivo")
    fileBytes = await file.read()
    embbeds = []
    try:
        embbeds = get_face_embbed(BytesIO(fileBytes), nome)
    except ValueError:
        raise HTTPException(status_code=400, detail="Nenhum rosto foi encontrado")
    nome_bytes = nome.encode('utf-8')[:99]  # Trunca se necessário
    for embbed in embbeds:
        novo_ponto = TReg(embed=embbed, nome=nome_bytes)
        lib.inserir_ponto(novo_ponto)
    return {"mensagem": f"Ponto '{nome}' inserido com sucesso."}

@app.post("/buscar")
async def buscar(embbed: UploadFile):
    fileBytes = await embbed.read()
    embbeds = get_face_embbed(BytesIO(fileBytes))
    resultados : list[dict] = []
    for embbed in embbeds:
        query = TReg(embed=embbed)
        arv = lib.get_tree()  # Suponha que esta função retorne ponteiro para árvore já construída
        resultado = lib.buscar_mais_proximo(arv, query)
        resultados.append({ "nome": resultado.nome, "embbed": [float(resultado.embed[i]) for i in range(128)] })
    return resultados
