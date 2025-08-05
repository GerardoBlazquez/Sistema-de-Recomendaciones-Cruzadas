
def boost_score(score, genero_compartido, generos_busqueda, item_genres):
    if genero_compartido:
        bonus = 1.2
        if generos_busqueda and item_genres and generos_busqueda[0] == item_genres[0]:
            bonus += 0.20
    else:
        bonus = 0.8
    return score * bonus