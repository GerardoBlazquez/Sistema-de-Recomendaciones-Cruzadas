import pandas as pd 


def es_valido(item, tipo_item):
    def faltante(val):
        return pd.isna(val) or str(val).strip().lower() in ["", "nan", "none", "sin datos"]

    descripcion = item.get("descripcion_castellano") or item.get("overview")
    poster = item.get("poster") or item.get("poster_url")
    director = item.get("director") if tipo_item == "pelicula" else None
    puntuacion = (
        item.get("puntuacion") or item.get("user_score") or item.get("product_rating")
        or item.get("average_rating") or item.get("vote_average")
    )
    campos_vacios = 0
    if faltante(descripcion) or "no disponible" in str(descripcion).lower():
        campos_vacios += 1
    if not isinstance(poster, str) or poster.lower() in ["none", "sin poster", ""]:
        campos_vacios += 1
    if tipo_item == "pelicula" and (faltante(director) or (director and director.lower() == "director desconocido")):
        campos_vacios += 1
    if pd.isna(puntuacion) or float(puntuacion) == 0.0:
        campos_vacios += 1
    return campos_vacios < 3
