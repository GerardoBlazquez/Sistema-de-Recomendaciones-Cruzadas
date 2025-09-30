import requests
import math

query = input("¿Qué título te gusta?: ")
tipo_origen = input("¿Qué tipo es ese contenido? (pelicula, serie, libro, videojuego): ").strip().lower()

# Aquí permitimos al usuario ingresar múltiples tipos separados por coma
tipo_destino_input = input("¿Qué tipo quieres que te recomiende? (pelicula, serie, libro, videojuego, todos) o múltiples separados por coma: ").strip().lower()

# Convertir entrada a lista si tiene comas, sino string ni se modifica
if tipo_destino_input == "todos":
    tipo_destino = "todos"
elif "," in tipo_destino_input:
    tipo_destino = [t.strip() for t in tipo_destino_input.split(",") if t.strip()]
else:
    tipo_destino = tipo_destino_input

try:
    top_k = int(input("¿Cuántas recomendaciones quieres?: "))
except ValueError:
    top_k = 5
    print("Número inválido. Se usarán 5 recomendaciones por defecto.")

print(f"\n... Buscando recomendaciones de tipo '{tipo_destino}' basadas en '{query}' ({tipo_origen})...")

data = {
    "query": query,
    "tipo_origen": tipo_origen,
    "tipo_destino": tipo_destino,
    "top_k": top_k
}

def mostrar_puntuacion(p):
    return "Puntuación no disponible" if p == 0.0 or p is None else f"{p:.2f}"

def mostrar_recomendacion(r):
    tipo = r.get("tipo", "desconocido")
    print(f"- [{tipo}] {r['titulo']} ({r.get('año', 'Año desconocido')})")
    print(f"  Descripción: {r.get('descripcion', 'Sin descripción disponible')}")

    puntuacion = r.get("puntuacion")
    if puntuacion is not None and not (isinstance(puntuacion, float) and math.isnan(puntuacion)):
        print(f"  Puntuación: {mostrar_puntuacion(puntuacion)}")

    genres = r.get("genres") or r.get("generos")
    if genres:
        if isinstance(genres, list):
            print(f"  Género: {', '.join(genres)}")
        else:
            print(f"  Género: {genres}")

    print(f"  Poster: {r.get('poster', 'No disponible')}")

    if tipo == "pelicula":
        companies = r.get("production_companies")
        director = r.get("director")
        if companies:
            if isinstance(companies, list):
                print(f"  Compañías productoras: {', '.join(companies)}")
            else:
                print(f"  Compañías productoras: {companies}")
        if director:
            print(f"  Director: {director}")

    elif tipo == "serie":
        companies = r.get("production_companies")
        director = r.get("director")
        if companies:
            if isinstance(companies, list):
                print(f"  Compañías productoras: {', '.join(companies)}")
            else:
                print(f"  Compañías productoras: {companies}")
        if director:
            print(f"  Director: {director}")

        temporadas = r.get("temporadas")
        if temporadas:
            print("  Temporadas:")
            for temp in temporadas:
                num = temp.get("season_number", "Desconocido")
                name = temp.get("name", "")
                aired = temp.get("air_date", "Fecha desconocida")
                episodes = temp.get("episode_count", "Nº desconocido")
                overview = temp.get("overview", "").strip()
                print(f"    - Temporada {num}: {name} | Estreno: {aired} | Episodios: {episodes}")
                if overview:
                    print(f"      Descripción: {overview}")

    elif tipo == "libro":
        autor = r.get("autor")
        if autor:
            print(f"  Autor: {autor}")

    elif tipo == "videojuego":
        platforms = r.get("platforms")
        developers = r.get("developers")

        if platforms:
            print(f"  Plataformas: {', '.join(platforms)}")
        if developers:
            if isinstance(developers, list):
                print(f"  Desarrolladores: {', '.join(developers)}")
            else:
                print(f"  Desarrolladores: {developers}")

    print()

try:
    response = requests.post("http://127.0.0.1:8000/recomendar", json=data)
    if response.status_code == 200:
        print("RECOMENDACIONES:")

        data = response.json().get("recomendaciones")

        if isinstance(data, dict) and "combinadas" in data and "por_tipo" in data:
            # Nuevos formatos con múltiples tipos
            print("\n-- Recomendaciones combinadas --")
            for r in data.get("combinadas", []):
                mostrar_recomendacion(r)

            print("\n-- Recomendaciones por tipo --")
            for tipo, lista in data.get("por_tipo", {}).items():
                print(f"\nTipo: {tipo}")
                for r in lista:
                    mostrar_recomendacion(r)

        else:
            # Formato simple (antes)
            if data is None:
                print("No se recibieron recomendaciones.")
            else:
                for r in data:
                    mostrar_recomendacion(r)

    else:
        print(f"Error ({response.status_code}): {response.json().get('mensaje', response.text)}")
except Exception as e:
    print(f"Error de conexión: {e}")
