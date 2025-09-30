import os 
import traceback 
import requests 
from rapidfuzz import process 





TMDB_API_KEY = os.getenv("TMDB_API_KEY") 
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY") 
RAWG_API_KEY = os.getenv("RAWG_API_KEY")
POSTER_BASE_URL = "https://image.tmdb.org/t/p/w500"



def obtener_info_pelicula_tmdb(titulo):
    try:
        url_search = "https://api.themoviedb.org/3/search/movie"
        params_search = {
            "api_key": TMDB_API_KEY,
            "query": titulo,
            "include_adult": "false",
            "language": "es-ES"
        }

        r_search = requests.get(url_search, params=params_search)
        if r_search.status_code == 200:
            data_search = r_search.json().get("results", [])
            if data_search:
                nombres_api = [res.get("title", "") for res in data_search]
                match_result = process.extractOne(titulo, nombres_api)
                if match_result:
                    match, score, idx = match_result

                    if score < 65:
                        print(f"Coincidencia baja con TMDb: '{match}' ({score}%)")
                        return _respuesta_vacia(titulo)

                    movie = data_search[idx]
                    movie_id = movie.get("id")
                    poster_path = movie.get("poster_path")
                    poster_url = POSTER_BASE_URL + poster_path if poster_path else None

                    # Obtener detalles
                    url_details = f"https://api.themoviedb.org/3/movie/{movie_id}"
                    params_details = {"api_key": TMDB_API_KEY, "language": "es-ES"}
                    r_details = requests.get(url_details, params=params_details)

                    if r_details.status_code == 200:
                        data_details = r_details.json()
                        production_companies = [comp.get("name") for comp in data_details.get("production_companies", [])]

                        # Director
                        url_credits = f"https://api.themoviedb.org/3/movie/{movie_id}/credits"
                        r_credits = requests.get(url_credits, params=params_details)
                        director = None
                        if r_credits.status_code == 200:
                            data_credits = r_credits.json()
                            for persona in data_credits.get("crew", []):
                                if persona.get("job") == "Director":
                                    director = persona.get("name")
                                    break

                        generos = [g["name"].lower() for g in data_details.get("genres", [])]

                        return {
                            "titulo": movie.get("title", titulo),
                            "poster": poster_url,
                            "production_companies": production_companies,
                            "director": director,
                            "descripcion": data_details.get("overview", "Descripción no disponible"),
                            "puntuacion": data_details.get("vote_average", 0.0),
                            "año": data_details.get("release_date", "")[:4],
                            "generos": generos
                        }

        # Si no hay respuesta válida
        print(f"No se encontraron datos válidos para '{titulo}' en TMDb.")
        return _respuesta_vacia(titulo)

    except Exception as e:
        print(f"Excepción en obtener_info_pelicula_tmdb('{titulo}'): {e}")
        traceback.print_exc()
        return _respuesta_vacia(titulo)

def _respuesta_vacia(titulo):
    return {
        "titulo": titulo,
        "poster": None,
        "production_companies": [],
        "director": None,
        "descripcion": "Descripción no disponible",
        "puntuacion": 0.0,
        "año": "",
        "generos": []
    }

def buscar_peliculas_por_genero_tmdb(genero, cantidad=10):

    GENERO_TMDB_IDS = {
    "horror": 27,
    "acción": 28,
    "drama": 18,
    "comedia": 35,
    "aventura": 12,
    "ciencia ficción": 878,
    "thriller": 53,
    "documental": 99,
    "crimen": 80,
    "romance": 10749,
    "misterio": 9648,
    "familia": 10751,
    "animación": 16,
    "fantasía": 14
}
   
    # Paso 1: Obtener todos los géneros con sus IDs desde TMDb
    url_generos = f"https://api.themoviedb.org/3/genre/movie/list"
    params_generos = {
        "api_key": TMDB_API_KEY,
        "language": "es-ES"
    }

    r_generos = requests.get(url_generos, params=params_generos)
    if r_generos.status_code != 200:
        print("No se pudo obtener la lista de géneros de TMDb.")
        return []

    generos_data = r_generos.json().get("genres", [])

    genero_id = GENERO_TMDB_IDS.get(genero.lower())
   
    if not genero_id:
        print(f"Género '{genero}' no reconocido en TMDb.")
        return []

    # Paso 2: Buscar películas del género, ordenadas por puntuación (con un mínimo de votos)
    url_discover = "https://api.themoviedb.org/3/discover/movie"
    params_discover = {
        "api_key": TMDB_API_KEY,
        "with_genres": genero_id,
        "language": "es-ES",
        "sort_by": "vote_average.desc",
        "vote_count.gte": 50,
        "include_adult": False,
        "page": 1
    }

    r_discover = requests.get(url_discover, params=params_discover)
    if r_discover.status_code != 200:
        print("Error al hacer la búsqueda en TMDb.")
        return []

    peliculas_raw = r_discover.json().get("results", [])[:cantidad]

    resultados = []
    for p in peliculas_raw:
        try:
            titulo = p.get("title")
            if not titulo or str(titulo).strip().lower() == 'nan':
                print(f"Título inválido: '{titulo}'")
                continue

            detalles = obtener_info_pelicula_tmdb(titulo)  # Usas tu función ya existente
            if detalles:
                resultados.append(detalles)
                if len(resultados) >= cantidad:
                    break
        except Exception as e:
            print(f"Error procesando película: {e}")
            continue

    return resultados


def obtener_info_serie_tmdb(titulo):
    try:
        url_search = "https://api.themoviedb.org/3/search/tv"
        params_search = {
            "api_key": TMDB_API_KEY,
            "query": titulo,
            "include_adult": "false",
            "language": "es-ES"
        }

        r_search = requests.get(url_search, params=params_search)
        if r_search.status_code == 200:
            data_search = r_search.json().get("results", [])
            if data_search:
                nombres_api = [res.get("name", "") for res in data_search]
                match_result = process.extractOne(titulo, nombres_api)
                if match_result:
                    match, score, idx = match_result

                    if score < 65:
                        print(f"Coincidencia baja con TMDb (serie): '{match}' ({score}%)")
                        return _respuesta_vacia(titulo)

                    serie = data_search[idx]
                    serie_id = serie.get("id")
                    poster_path = serie.get("poster_path")
                    poster_url = POSTER_BASE_URL + poster_path if poster_path else None

                    # Puede venir sin first_air_date correcto en la búsqueda simple
                    fecha_str = serie.get("first_air_date", "")
                    año = fecha_str[:4] if fecha_str and len(fecha_str) >= 4 else ""

                    # Si falta año (o info clave), hacer el request de detalles para completar datos
                    if not año:
                        url_details = f"https://api.themoviedb.org/3/tv/{serie_id}"
                        params_details = {"api_key": TMDB_API_KEY, "language": "es-ES"}
                        r_details = requests.get(url_details, params=params_details)
                        if r_details.status_code == 200:
                            data_details = r_details.json()
                            fecha_str = data_details.get("first_air_date", "")
                            año = fecha_str[:4] if fecha_str and len(fecha_str) >= 4 else ""
                        else:
                            data_details = {}
                    else:
                        data_details = {}

                    # Si no hicimos request detalles antes, lo hacemos igual para extraer info completa
                    if not data_details:
                        url_details = f"https://api.themoviedb.org/3/tv/{serie_id}"
                        params_details = {"api_key": TMDB_API_KEY, "language": "es-ES"}
                        r_details = requests.get(url_details, params=params_details)
                        if r_details.status_code == 200:
                            data_details = r_details.json()
                        else:
                            data_details = {}

                    production_companies = [comp.get("name") for comp in data_details.get("production_companies", [])]

                    director = None
                    url_credits = f"https://api.themoviedb.org/3/tv/{serie_id}/credits"
                    r_credits = requests.get(url_credits, params=params_details)
                    if r_credits.status_code == 200:
                        data_credits = r_credits.json()
                        for persona in data_credits.get("crew", []):
                            if persona.get("job", "").lower() == "director":
                                director = persona.get("name")
                                break

                    generos = [g["name"].lower() for g in data_details.get("genres", [])]

                    temporadas = []
                    for temp in data_details.get("seasons", []):
                        temporadas.append({
                            "season_number": temp.get("season_number"),
                            "air_date": temp.get("air_date"),
                            "episode_count": temp.get("episode_count"),
                            "name": temp.get("name"),
                            "overview": temp.get("overview")
                        })

                    return {
                        "titulo": serie.get("name", titulo),
                        "poster": poster_url,
                        "production_companies": production_companies,
                        "director": director,
                        "descripcion": data_details.get("overview", "Descripción no disponible"),
                        "puntuacion": data_details.get("vote_average", 0.0),
                        "año": año,
                        "generos": generos,
                        "temporadas": temporadas
                    }

        print(f"No se encontraron datos válidos para serie '{titulo}' en TMDb.")
        return _respuesta_vacia(titulo)

    except Exception as e:
        print(f"Excepción en obtener_info_serie_tmdb('{titulo}'): {e}")
        traceback.print_exc()
        return _respuesta_vacia(titulo)




def buscar_series_por_genero_tmdb(genero, cantidad=10):

    GENERO_TMDB_IDS = {
        "drama": 18,
        "comedia": 35,
        "animación": 16,
        "aventura": 10759,
        "ciencia ficción": 10765,
        "reality": 10764,
        "familia": 10751,
        "misterio": 9648,
        "documental": 99,
        "crimen": 80,
        "fantasía": 10765,
        "thriller": 53,
        "romance": 10749,
        # Agrega más géneros TMDb para series según sea necesario
    }

    genero_id = GENERO_TMDB_IDS.get(genero.lower())
    if not genero_id:
        print(f"Género '{genero}' no reconocido en TMDb para series.")
        return []

    url_generos = "https://api.themoviedb.org/3/genre/tv/list"
    params_generos = {
        "api_key": TMDB_API_KEY,
        "language": "es-ES"
    }

    r_generos = requests.get(url_generos, params=params_generos)
    if r_generos.status_code != 200:
        print("No se pudo obtener la lista de géneros de series de TMDb.")
        return []

    generos_data = r_generos.json().get("genres", [])

    url_discover = "https://api.themoviedb.org/3/discover/tv"
    params_discover = {
        "api_key": TMDB_API_KEY,
        "with_genres": genero_id,
        "language": "es-ES",
        "sort_by": "vote_average.desc",
        "vote_count.gte": 50,
        "include_adult": False,
        "page": 1
    }

    r_discover = requests.get(url_discover, params=params_discover)
    if r_discover.status_code != 200:
        print("Error al hacer la búsqueda de series en TMDb.")
        return []

    series_raw = r_discover.json().get("results", [])[:cantidad]

    resultados = []
    for s in series_raw:
        try:
            titulo = s.get("name")
            if not titulo or str(titulo).strip().lower() == 'nan':
                print(f"Título inválido: '{titulo}'")
                continue

            detalles = obtener_info_serie_tmdb(titulo)
            if detalles:
                resultados.append(detalles)
                if len(resultados) >= cantidad:
                    break
        except Exception as e:
            print(f"Error procesando serie: {e}")
            continue

    return resultados
