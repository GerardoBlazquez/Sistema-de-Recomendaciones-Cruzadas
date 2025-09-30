from constantes import PALABRAS_CLAVE_ESPECIAL, GENEROS_FORZADOS, COMBINACIONES_PROHIBIDAS, tipo_pesos, traducciones
from utils import normalizar_titulo, mapear_genero, parsear_generos, mapear_generos_item
from validacion import es_valido
from cache import obtener_info_externa_cache, api_cache
from index import get_index_and_metadata
from scoring import boost_score

import os 
import traceback 
import pandas as pd 
import numpy as np 
from sentence_transformers import SentenceTransformer 
import faiss 
import pickle 
import requests 
from flask import Flask, request, jsonify 
from rapidfuzz import process 
import re 
import unidecode
import json
import threading
import concurrent.futures
from flask_cors import CORS


MODEL_NAME = "all-MiniLM-L6-v2"
model = SentenceTransformer(MODEL_NAME)


def eliminar_duplicados(recomendaciones, titulo_origen):
    titulos_vistos = set()
    titulo_origen_norm = normalizar_titulo(titulo_origen)
    filtradas = []
    for r in recomendaciones:
        n = normalizar_titulo(r.get("titulo", ""))
        if not n or n == titulo_origen_norm:
            continue
        if n not in titulos_vistos:
            titulos_vistos.add(n)
            filtradas.append(r)
    return filtradas

def buscar_recomendaciones(query, tipo_origen="pelicula", tipo_destino="pelicula", top_k=5, genero=None, intentos=0):
    print(f"Buscando en dataset: '{query}' (intento {intentos + 1})")
    titulo_norm = normalizar_titulo(query)

    # Normalizar tipo_destino a lista de tipos válidos
    if tipo_destino == "todos":
        tipos = ["pelicula", "serie", "libro", "videojuego"]
    elif isinstance(tipo_destino, str):
        tipos = [tipo_destino.lower()]
    elif isinstance(tipo_destino, list):
        tipos = [t.lower() for t in tipo_destino]
    else:
        raise ValueError("tipo_destino debe ser str o lista de str")

    # Caso múltiples tipos: búsqueda paralela y combinación con resultados inmediatos
    if len(tipos) > 1:
        top_por_tipo = max(1, top_k // len(tipos))
        recomendaciones_por_tipo = {}

        with concurrent.futures.ThreadPoolExecutor(max_workers=len(tipos)) as executor:
            future_to_tipo = {
                executor.submit(buscar_recomendaciones, query, tipo_origen, t, top_por_tipo, genero, intentos): t
                for t in tipos
            }

            for future in concurrent.futures.as_completed(future_to_tipo):
                t = future_to_tipo[future]
                try:
                    res = future.result()
                    if res:
                        res.sort(key=lambda x: (x.get("score", 1.0), x.get("puntuacion", 0)), reverse=True)

                        recomendaciones_por_tipo[t] = res

                        print(f"\n Recomendaciones para tipo '{t}':", flush=True)
                        for r in res:
                            print(f"- [{r['tipo']}] {r['titulo']} ({r.get('año', 'Año desconocido')})", flush=True)

                except Exception as e:
                    print(f"Error en búsqueda para tipo '{t}': {e}", flush=True)

        # Combinación y ordenación final de todas las recomendaciones
        todas = []
        for lst in recomendaciones_por_tipo.values():
            todas.extend(lst)

        for r in todas:
            r["score"] = r.get("score", 1.0) * tipo_pesos.get(r.get("tipo"), 1.0)
            r["puntuacion"] = 0 if pd.isna(r.get("puntuacion")) else float(r.get("puntuacion"))

        todas = eliminar_duplicados(todas, titulo_norm)
        todas.sort(key=lambda x: (x["score"], x["puntuacion"]), reverse=True)

        # Devuelve dict con resultados por tipo y todas combinadas
        return {
            "por_tipo": recomendaciones_por_tipo,
            "combinadas": todas[:top_k]
        }

    # Caso un solo tipo: código actual, sin cambios
    tipo_dest_busqueda = tipos[0]

    index, media_metadata = get_index_and_metadata(tipo_dest_busqueda)
    if index is None or media_metadata is None:
        print(" No se pudo cargar o crear índice.")
        return []

    info = obtener_info_externa_cache(tipo_origen, query)
    generos_forzados = GENEROS_FORZADOS.get(titulo_norm)
    generos_busqueda = []
    query_text = query
    if generos_forzados:
        print(f" Usando géneros forzados para '{query}': {generos_forzados}")
        generos_busqueda = generos_forzados
    else:
        if info and isinstance(info, dict):
            if info.get("generos") and isinstance(info["generos"], list):
                generos_busqueda = [g.lower() for g in info["generos"][:3]]
                print(f" Géneros extraídos: {generos_busqueda}")
            if info.get("descripcion"):
                query_text = info["descripcion"]
                print(" Usando descripción para embedding")

    if genero:
        generos_busqueda.append(mapear_genero(genero))

    generos_busqueda = list(dict.fromkeys([mapear_genero(g) for g in generos_busqueda]))
    if "documentary" in generos_busqueda or tipo_dest_busqueda == "videojuego":
        generos_busqueda = []
    print(f" Géneros finales: {generos_busqueda}")

    query_emb = model.encode([query_text])
    query_emb = np.array(query_emb).astype("float32")
    faiss.normalize_L2(query_emb)
    D, I = index.search(query_emb, top_k * 15)

    recomendaciones = []
    titulo_base_norm = normalizar_titulo(info.get("titulo", query) if info else query)
    MAX_API = 10
    titulos_vistos = set()

    # Añadimos primero la info completa del título base buscado
    if info and info.get("titulo"):
        rec_base = {
            "titulo": info.get("titulo"),
            "año": info.get("año") or info.get("year") or "Año desconocido",
            "descripcion": info.get("descripcion") or "",
            "puntuacion": float(info.get("puntuacion") or 0),
            "poster": info.get("poster") or "",
            "tipo": tipo_origen,
            "score": 1.0,  # Máxima relevancia para el título buscado
            "generos": info.get("generos") or info.get("genres") or [],
        }
        recomendaciones.append(rec_base)
        titulos_vistos.add(normalizar_titulo(rec_base["titulo"]))
        if top_k == 1:
            return recomendaciones

    for pos, (score, idx) in enumerate(zip(D[0], I[0])):
        if idx == -1:
            continue
        item = media_metadata[idx]
        tipo_item = str(item.get("tipo", "")).lower()
        if tipo_item != tipo_dest_busqueda:
            continue

        item_genres = mapear_generos_item(item.get("genres") or item.get("generos") or [])
        if not item_genres:
            try:
                external_info = obtener_info_externa_cache(tipo_item, item.get("titulo") or item.get("title"))
                if external_info:
                    new_genres = external_info.get("generos") or external_info.get("genres") or []
                    item_genres = [mapear_genero(g) for g in (new_genres if isinstance(new_genres, list) else [])]
                    item["generos"] = new_genres
            except Exception as e:
                print(f"Error obteniendo géneros por API externa para '{item.get('titulo','')}': {e}")

        item_genres = item_genres[:3]
        item_genres_set = set(item_genres)
        palabras_clave = []
        for gkk in generos_busqueda:
            if gkk in PALABRAS_CLAVE_ESPECIAL:
                palabras_clave = PALABRAS_CLAVE_ESPECIAL[gkk]
                break

        titulo = item.get("titulo_castellano") or item.get("title") or ""
        descripcion = item.get("descripcion_castellano") or item.get("overview") or ""
        poster = item.get("poster") or item.get("poster_url")
        if not isinstance(titulo, str) or not isinstance(descripcion, str):
            continue
        if not titulo.strip() or not descripcion.strip() or titulo.lower().strip() == "nan" or descripcion.lower().strip() == "nan":
            continue

        keywords_raw = item.get("keywords", "")
        if isinstance(keywords_raw, str):
            keywords = [k.strip().lower() for k in keywords_raw.split(",") if k.strip()]
        elif isinstance(keywords_raw, list):
            keywords = [k.lower() for k in keywords_raw]
        else:
            keywords = []
        text_descr = descripcion.lower().strip()

        if palabras_clave:
            if text_descr and len(text_descr) > 20:
                if not any(pal.lower() in text_descr for pal in palabras_clave):
                    combined_text = titulo.lower() + " " + " ".join(keywords)
                    if not any(pal.lower() in combined_text for pal in palabras_clave):
                        puntuacion_actual = float(item.get("puntuacion") or 0)
                        genero_compartido = bool(set(item_genres) & set(generos_busqueda)) if generos_busqueda else True
                        if not genero_compartido and puntuacion_actual < 5.0:
                            print(f" Rechazado por filtro palabras clave y sin género/puntuación suficiente: {titulo}")
                            continue
                        else:
                            print(f" No cumple palabras clave pero pasa por género/puntuación: {titulo}")
            else:
                print(f" Descripción corta o vacía: {titulo}")

        if any(prohibido.issubset(item_genres_set) for prohibido in COMBINACIONES_PROHIBIDAS):
            continue
        genero_compartido = bool(set(item_genres) & set(generos_busqueda)) if generos_busqueda else True
        if generos_busqueda and not genero_compartido:
            if not (palabras_clave and any(pal.lower() in text_descr for pal in palabras_clave)):
                print(f"Rechazado por no compartir género ni palabras clave: {titulo}")
                continue

        score_modificado = boost_score(score, genero_compartido, generos_busqueda, item_genres)

        if pos < MAX_API:
            info_ext = obtener_info_externa_cache(tipo_item, titulo)
        else:
            info_ext = None

        author, year_pub, prod_companies, devs, director = None, None, [], [], None
        if info_ext:
            titulo = info_ext.get("titulo") or titulo
            descripcion = info_ext.get("descripcion") or descripcion
            poster = info_ext.get("poster") or poster
            new_genres = info_ext.get("generos") or info_ext.get("genres") or []
            if new_genres:
                item_genres = [mapear_genero(g) for g in new_genres if g]
            if tipo_item in ("pelicula", "serie"):
                prod_companies = info_ext.get("production_companies") or []
                director = info_ext.get("director") or director
            elif tipo_item == "libro":
                author = info_ext.get("autor")
                year_pub = info_ext.get("año")
            elif tipo_item == "videojuego":
                devs = info_ext.get("developers") or []

        if not descripcion or not poster:
            continue

        item["descripcion_castellano"] = descripcion
        item["poster_url"] = poster
        item["director"] = director
        if item.get("puntuacion") is None and info_ext:
            item["puntuacion"] = info_ext.get("puntuacion")
        if not es_valido(item, tipo_item):
            continue

        year_cand = info_ext.get("año") if info_ext else None
        if not year_cand:
            year_cand = info_ext.get("year") if info_ext else None
        if not year_cand:
            year_cand = year_pub or item.get("year")
        try:
            yr = int(float(year_cand))
            if yr <= 1800 or yr > 2100:
                yr = None
        except Exception:
            yr = None

        rec = {
            "titulo": titulo,
            "año": yr or "Año desconocido",
            "descripcion": descripcion,
            "puntuacion": float(item.get("puntuacion") or 0),
            "poster": poster,
            "tipo": tipo_item,
            "score": float(score_modificado * tipo_pesos.get(tipo_item, 1.0)),
            "generos": item_genres,
        }
        if tipo_item == "pelicula":
            rec["production_companies"] = prod_companies
            rec["director"] = director
        elif tipo_item == "serie":
            rec["production_companies"] = prod_companies
            rec["director"] = director
            if info_ext and "temporadas" in info_ext:
                rec["temporadas"] = info_ext["temporadas"]
        elif tipo_item == "libro":
            rec["autor"] = author
        elif tipo_item == "videojuego":
            rec["developers"] = devs

        norm_titulo = normalizar_titulo(titulo)
        if norm_titulo == titulo_base_norm or norm_titulo in titulos_vistos:
            continue
        titulos_vistos.add(norm_titulo)
        recomendaciones.append(rec)

    if len(recomendaciones) >= top_k:
        recomendaciones = eliminar_duplicados(recomendaciones, titulo_base_norm)
        recomendaciones.sort(key=lambda x: (x["score"], x["puntuacion"]), reverse=True)
        return recomendaciones[:top_k]

    # Intento 1 - fallback con API externa
    if intentos == 1:
        reco_api = []
        api_info = obtener_info_externa_cache(tipo_origen, query)
        if api_info and api_info.get("titulo"):
            reco_api.append({
                "titulo": api_info.get("titulo"),
                "descripcion": api_info.get("descripcion") or "",
                "puntuacion": float(api_info.get("puntuacion") or 0),
                "poster": api_info.get("poster") or "",
                "tipo": tipo_origen,
                "score": 0.7,
                "generos": api_info.get("generos") or []
            })
        if reco_api:
            return reco_api[:top_k]
        return buscar_recomendaciones(query, tipo_origen, tipo_destino, top_k, genero, intentos=2)

    # Intento 2 - fallback ampliado
    if intentos == 2:
        fallback_gens = []
        if info and info.get("generos"):
            fallback_gens = [g.lower() for g in info.get("generos")]
        else:
            fallback_gens_map = {
                "pelicula": ["action", "adventure", "fantasy", "science fiction"],
                "serie": ["drama", "comedy", "fantasy", "mystery", "superhero", "marvel"],
                "libro": ["fantasy", "romance", "mystery"],
                "videojuego": ["action", "adventure", "rpg", "shooter"],
            }
            fallback_gens = fallback_gens_map.get(tipo_dest_busqueda, [])
        if not fallback_gens:
            fallback_gens = [""]

        text_to_embedding = (info.get("descripcion") or "") + " " + (info.get("titulo") or "")
        query_emb = model.encode([text_to_embedding])
        query_emb = np.array(query_emb).astype("float32")
        faiss.normalize_L2(query_emb)
        D, I = index.search(query_emb, top_k * 20)
        recomendaciones_relajadas = []
        for score, idx in zip(D[0], I[0]):
            if idx == -1:
                continue
            item = media_metadata[idx]
            tipo_item = str(item.get("tipo", "")).lower()
            if tipo_item != tipo_dest_busqueda:
                continue

            item_genres = mapear_generos_item(item.get("genres") or item.get("generos") or [])
            if not any(g in fallback_gens for g in item_genres):
                continue

            titulo = item.get("titulo_castellano") or item.get("title") or ""
            descripcion = item.get("descripcion_castellano") or item.get("overview") or ""
            poster = item.get("poster") or item.get("poster_url")
            if not isinstance(titulo, str) or not isinstance(descripcion, str):
                continue
            if not titulo.strip() or not descripcion.strip() or titulo.lower().strip() == "nan" or descripcion.lower().strip() == "nan":
                continue

            reco_rel = {
                "titulo": titulo,
                "descripcion": descripcion,
                "puntuacion": float(item.get("puntuacion") or 0),
                "poster": poster,
                "tipo": tipo_item,
                "score": score * 0.5,
                "generos": item_genres if item_genres else ["Género desconocido"]
            }
            recomendaciones_relajadas.append(reco_rel)
            if len(recomendaciones_relajadas) >= top_k:
                break

        if recomendaciones_relajadas:
            recomendaciones_relajadas = eliminar_duplicados(recomendaciones_relajadas, titulo_base_norm)
            recomendaciones_relajadas.sort(key=lambda x: (x["score"], x["puntuacion"]), reverse=True)
            return recomendaciones_relajadas[:top_k]

    recomendaciones = eliminar_duplicados(recomendaciones, titulo_base_norm)
    recomendaciones.sort(key=lambda x: (x["score"], x["puntuacion"]), reverse=True)
    return recomendaciones[:top_k]
