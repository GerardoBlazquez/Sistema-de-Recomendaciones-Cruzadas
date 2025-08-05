import traceback 
from api.tmdb import obtener_info_pelicula_tmdb, obtener_info_serie_tmdb
from api.google_books import buscar_libro_google
from api.videojuegos import buscar_videojuego_rawg

api_cache = {}

def obtener_info_externa_cache(tipo, titulo):
    key = (tipo, titulo.lower().strip())
    if key in api_cache:
        return api_cache[key]
    try:
        if tipo == "pelicula":
            result = obtener_info_pelicula_tmdb(titulo)
        elif tipo == "serie":
            result = obtener_info_serie_tmdb(titulo)
        elif tipo == "libro":
            result = buscar_libro_google(titulo)
        elif tipo == "videojuego":
            result = buscar_videojuego_rawg(titulo)
        else:
            result = None
    except Exception as e:
        print(f"❌ Error API externa [{tipo}]: '{titulo}': {e}")
        traceback.print_exc()
        result = None
    api_cache[key] = result
    return result