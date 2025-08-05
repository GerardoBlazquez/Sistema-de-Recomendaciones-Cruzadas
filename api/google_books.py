import os 
import requests 
import re 




TMDB_API_KEY = os.getenv("TMDB_API_KEY") 
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY") 
RAWG_API_KEY = os.getenv("RAWG_API_KEY")
POSTER_BASE_URL = "https://image.tmdb.org/t/p/w500"



def buscar_libro_google(title):
    def extraer_info_libro(info):
        autor = ", ".join(info.get("authors", [])) if info.get("authors") else "Autor desconocido"
        published = info.get("publishedDate", "")
        match = re.search(r"\d{4}", published)
        year = int(match.group()) if match else None

        generos = [c.lower() for c in info.get("categories", [])]  # géneros desde "categories"

        return {
            "titulo": info.get("title"),
            "descripcion": info.get("description", "Sin descripción disponible"),
            "poster": info.get("imageLinks", {}).get("thumbnail", "Sin poster"),
            "autor": autor,
            "año": year,
            "generos": generos
        }

    params = {
        "q": title,
        "langRestrict": "es",
        "printType": "books",
        "maxResults": 1,
        "key": GOOGLE_API_KEY
    }

    try:
        r = requests.get("https://www.googleapis.com/books/v1/volumes", params=params)
        if r.status_code == 200:
            data = r.json()
            if data.get("totalItems", 0) > 0:
                info = data["items"][0].get("volumeInfo", {})
                return extraer_info_libro(info)

        # Fallback sin restricción de idioma
        params.pop("langRestrict")
        r_fallback = requests.get("https://www.googleapis.com/books/v1/volumes", params=params)
        if r_fallback.status_code == 200:
            data_fallback = r_fallback.json()
            if data_fallback.get("totalItems", 0) > 0:
                info = data_fallback["items"][0].get("volumeInfo", {})
                return extraer_info_libro(info)

    except Exception as e:
        print(f"❌ Error al buscar libro: {e}")

    return None


def buscar_libros_por_genero_google(genero, cantidad=10):
    url = "https://www.googleapis.com/books/v1/volumes"
    params = {
        "q": f"subject:{genero}",
        "printType": "books",
        "langRestrict": "es",
        "maxResults": min(cantidad, 40),  # Google Books max 40 por request
        "key": GOOGLE_API_KEY
    }

    r = requests.get(url, params=params)
    if r.status_code != 200:
        print("❌ Error al hacer la búsqueda en Google Books.")
        return []

    items = r.json().get("items", [])
    resultados = []

    for item in items[:cantidad]:
        volume_info = item.get("volumeInfo", {})
        titulo = volume_info.get("title")
        descripcion = volume_info.get("description") or volume_info.get("subtitle") or ""
        autores = volume_info.get("authors", [])
        año = volume_info.get("publishedDate", "")[:4]
        poster = None

        # Intentar extraer imagen
        image_links = volume_info.get("imageLinks")
        if image_links:
            poster = image_links.get("thumbnail") or image_links.get("smallThumbnail")

        # Obtener géneros, puede estar vacío
        generos = [c.lower() for c in volume_info.get("categories", [])]

        # Si no hay géneros, incluye el libro igual con advertencia
        if not generos:
            print(f"⚠️ Libro sin géneros definidos: {titulo}, incluyendo de todas formas.")
            generos = [genero.lower()]
        else:
            # Filtrar libros que tengan el género deseado
            if genero.lower() not in generos:
                continue

        resultados.append({
            "titulo": titulo,
            "descripcion": descripcion,
            "autor": ", ".join(autores) if autores else None,
            "año": int(año) if año.isdigit() else None,
            "poster": poster,
            "tipo": "libro",
            "puntuacion": None,  # No hay puntuación directa en Google Books
            "generos": generos
        })

    return resultados




