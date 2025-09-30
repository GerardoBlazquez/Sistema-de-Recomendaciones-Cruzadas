import os 

import requests 
from rapidfuzz import process 


TMDB_API_KEY = os.getenv("TMDB_API_KEY") 
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY") 
RAWG_API_KEY = os.getenv("RAWG_API_KEY")
POSTER_BASE_URL = "https://image.tmdb.org/t/p/w500"




def buscar_videojuego_rawg(title):
    try:
        params = {"key": RAWG_API_KEY, "search": title, "page_size": 5}
        r = requests.get("https://api.rawg.io/api/games", params=params)
        r.raise_for_status()
        data = r.json()
        resultados = data.get("results", [])
        if resultados:
            nombres = [g["name"] for g in resultados]
            match, score, idx = process.extractOne(title, nombres)

            if score < 65:
                print(f"Coincidencia baja con RAWG: '{match}' ({score}%)")
                return None

            game = resultados[idx]
            detail_url = f"https://api.rawg.io/api/games/{game['id']}"
            detail_resp = requests.get(detail_url, params={"key": RAWG_API_KEY})
            detail_resp.raise_for_status()
            detail_data = detail_resp.json()

            platforms = [plat["platform"]["name"] for plat in detail_data.get("platforms", [])]
            developers = [dev["name"] for dev in detail_data.get("developers", [])]

            generos = [g["name"].lower() for g in detail_data.get("genres", [])]

            return {
                "titulo": detail_data.get("name"),
                "descripcion": detail_data.get("description_raw", "Sin descripción disponible"),
                "poster": detail_data.get("background_image", "Sin poster"),
                "puntuacion": detail_data.get("rating", "N/A"),
                "platforms": platforms,
                "developers": developers,
                "generos": generos
            }
    except Exception as e:
        print(f"Error RAWG: {e}")

    return None


def obtener_generos_rawg():
    return {
        "horror": ["horror", "survival-horror", "psychological-horror"],
        "accion": ["action", "action-rpg", "beat-em-up", "fighting", "shooter", "platformer", "hack-and-slash", "stealth"],
        "aventura": ["adventure", "point-and-click", "visual-novel", "interactive-fiction"],
        "rol": ["rpg", "action-rpg", "jrpg", "tactical-rpg", "roguelike"],
        "estrategia": ["strategy", "real-time-strategy", "turn-based-strategy", "tower-defense"],
        "simulacion": ["simulation", "life-simulation", "vehicle-simulation", "farming-sim", "sports"],
        "deportes": ["sports", "racing", "fighting"],
        "multijugador": ["multiplayer", "co-op", "massively-multiplayer"],
        "indie": ["indie"],
        "puzzle": ["puzzle"],
        "plataformas": ["platformer", "2d-platformer", "3d-platformer"],
        "terror": ["horror", "survival-horror", "psychological-horror"],
        "disparos": ["shooter", "first-person-shooter", "third-person-shooter"],
        "carreras": ["racing"],
        "sandbox": ["sandbox", "open-world"],
        "aventura-grafica": ["point-and-click", "adventure"],
        "arcade": ["arcade"],
        "musical": ["music", "rhythm"],
    }

def buscar_videojuegos_por_genero_rawg(genero, cantidad=10):
    generos_rawg = obtener_generos_rawg()
    if genero not in generos_rawg:
        print(f"Género RAWG desconocido: {genero}")
        return []

    resultados = []
    try:
        for gen in generos_rawg[genero]:
            params = {"key": RAWG_API_KEY, "genres": gen, "page_size": cantidad}
            r = requests.get("https://api.rawg.io/api/games", params=params)
            r.raise_for_status()
            data = r.json()
            for juego in data.get("results", []):
                resultados.append({
                    "titulo": juego.get("name"),
                    "descripcion": juego.get("description_raw", "Sin descripción"),
                    "poster": juego.get("background_image"),
                    "puntuacion": juego.get("rating", 0.0),
                    "generos": [gen]
                })
                if len(resultados) >= cantidad:
                    break
            if len(resultados) >= cantidad:
                break
    except Exception as e:
        print(f"Error al obtener juegos por género RAWG: {e}")

    return resultados

