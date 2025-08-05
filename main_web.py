import os

from flask import Flask, request, jsonify
from flask_cors import CORS
from sentence_transformers import SentenceTransformer
from rapidfuzz import fuzz
from unidecode import unidecode
import threading

import utils
import recomendador
import constantes
import index
import cache
import validacion
import scoring

from constantes import PALABRAS_CLAVE_ESPECIAL, GENEROS_FORZADOS, COMBINACIONES_PROHIBIDAS, tipo_pesos, traducciones
from utils import normalizar_titulo, mapear_genero, parsear_generos, mapear_generos_item
from validacion import es_valido
from cache import obtener_info_externa_cache, api_cache
from recomendador import eliminar_duplicados, buscar_recomendaciones
from index import crear_o_cargar_indice, get_index_and_metadata
from scoring import boost_score


app = Flask(__name__)
CORS(app)

@app.route("/", methods=["GET"])
def healthcheck():
    return {"status": "ok", "message": "Sistema de recomendación activo"}

@app.route("/recomendar", methods=["POST"])
def recomendar():
    data = request.json
    # Los nombres de campos deben coincidir con los esperados internamente
    query = data.get("query") or data.get("titulo")   # Soporta ambos posibles nombres
    tipo_origen = data.get("tipo_origen", "pelicula").lower()
    tipo_destino = data.get("tipo_destino", "pelicula")  # Puede ser lista o string, se maneja en recomendador
    genero = data.get("genero", None)
    top_k = int(data.get("top_k", 5))

    if not query or not tipo_origen or not tipo_destino:
        return jsonify({"error": "Faltan parámetros obligatorios: 'query' y 'tipo_origen'/'tipo_destino'"}), 400

    recomendaciones = buscar_recomendaciones(
        query,
        tipo_origen=tipo_origen,
        tipo_destino=tipo_destino,
        top_k=top_k,
        genero=genero,
    )
    if not recomendaciones:
        return jsonify({"mensaje": "No se encontraron recomendaciones."}), 404

    return jsonify({"recomendaciones": recomendaciones})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)