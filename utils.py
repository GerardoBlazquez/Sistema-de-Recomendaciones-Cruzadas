import json
from rapidfuzz import process
import unidecode
from constantes import traducciones





def normalizar_titulo(titulo):
    if not isinstance(titulo, str):
        return ""
    return unidecode.unidecode(titulo.lower().strip())




def mapear_genero(g):
    if not isinstance(g, str):
        return ""
    return traducciones.get(g.lower(), g.lower())


def parsear_generos(generos_raw, mapear=mapear_genero):
    if not generos_raw:
        return []
    try:
        # prevent errors on malformed json or empty strings
        if isinstance(generos_raw, str):
            generos_raw = generos_raw.strip()
            if not generos_raw or generos_raw.lower() == 'nan':
                return []
            generos = json.loads(generos_raw)
            if isinstance(generos, list):
                return [mapear(g.get("name", "") if isinstance(g, dict) else str(g)) for g in generos]
        elif isinstance(generos_raw, list):
            if all(isinstance(g, dict) and "name" in g for g in generos_raw):
                return [mapear(g.get("name", "")) for g in generos_raw]
            else:
                return [mapear(str(g)) for g in generos_raw if g]
        return []
    except Exception as e:
        print(f"⚠️ Error parseando géneros: {e}")
        return []


def mapear_generos_item(item_genres_raw):
    if not item_genres_raw:
        return []
    if isinstance(item_genres_raw, str):
        return parsear_generos(item_genres_raw)
    elif isinstance(item_genres_raw, list):
        return [mapear_genero(g) for g in item_genres_raw if isinstance(g, str)]
    else:
        return []