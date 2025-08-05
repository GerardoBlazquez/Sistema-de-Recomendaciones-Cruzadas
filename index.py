import os
import urllib.request
import pandas as pd
import numpy as np
import pickle
import faiss
from flask import Flask, request, jsonify
from flask_cors import CORS
from sentence_transformers import SentenceTransformer
from rapidfuzz import fuzz
from unidecode import unidecode
import threading

DATASET_FILE = "dataset_fusionado_final_7.csv"
DATASET_URL = "https://drive.google.com/uc?export=download&id=1brYWtJAP_eU0Ya3jC6hWAgPPjctzHjAU"
MODEL_NAME = "all-MiniLM-L6-v2"



if not os.path.exists(DATASET_FILE):
    print(f"📥 Descargando dataset desde {DATASET_URL}...")
    urllib.request.urlretrieve(DATASET_URL, DATASET_FILE)



model = SentenceTransformer(MODEL_NAME)
INDICES_GLOBALES = {}
METADATA_GLOBAL = {}



# ---------------------
# Cargar dataset y modelo
# ---------------------
def cargar_dataset():
    print("📂 Cargando dataset...")
    df = pd.read_csv(DATASET_FILE, low_memory=False)
    if "tipo" not in df.columns:
        raise ValueError("El dataset debe tener la columna 'tipo'.")
    def seleccionar_descripcion(row):
        if row["tipo"] == "pelicula":
            return row.get("overview", "")
        else:
            return row.get("descripcion_castellano", "")
    df["overview"] = df.apply(seleccionar_descripcion, axis=1).fillna("")
    return df

df = cargar_dataset()
# Ejemplo: función crear_o_cargar_indice corregida

def crear_o_cargar_indice(tipo_filtrado):
    tipos_validos = ['pelicula', 'serie', 'libro', 'videojuego']
    if tipo_filtrado not in tipos_validos:
        print(f"❌ Tipo inválido: '{tipo_filtrado}'. Debe ser uno de {tipos_validos}.")
        return None, None

    index_file = f"{tipo_filtrado}.index"
    metadata_file = f"{tipo_filtrado}_metadata.pkl"

    # Intentar cargar índice y metadatos ya existentes
    if os.path.exists(index_file) and os.path.exists(metadata_file):
        print(f"✅ Cargando índice FAISS existente para tipo '{tipo_filtrado}'...")
        try:
            index = faiss.read_index(index_file)
            with open(metadata_file, "rb") as f:
                media_metadata = pickle.load(f)
            return index, media_metadata
        except Exception as e:
            print(f"❌ Error al cargar el índice o metadatos: {e}")
            return None, None

    # Si no existen, crear embeddings y FAISS index
    print(f"⚙️ Creando embeddings y FAISS index para tipo '{tipo_filtrado}'...")
    df_filtrado = df[df["tipo"].str.lower() == tipo_filtrado]

    if df_filtrado.empty:
        print(f"⚠️ No hay datos del tipo '{tipo_filtrado}' en el dataset.")
        return None, None

    textos = df_filtrado["overview"].fillna("").tolist()

    try:
        # Generar embeddings
        embeddings = model.encode(textos, batch_size=64, show_progress_bar=True)
        embeddings = np.array(embeddings, dtype="float32")

        # Normalizar para similitud coseno (producto interno)
        faiss.normalize_L2(embeddings)

        # Crear índice FAISS
        dimension = embeddings.shape[1]
        index = faiss.IndexFlatIP(dimension)
        index.add(embeddings)

        # Guardar índice y metadatos
        faiss.write_index(index, index_file)
        media_metadata = df_filtrado.to_dict(orient="records")
        with open(metadata_file, "wb") as f:
            pickle.dump(media_metadata, f)

        print(f"✅ Índice creado con {len(media_metadata)} elementos.")
        return index, media_metadata

    except Exception as e:
        print(f"❌ Error al crear índice FAISS: {e}")
        return None, None

