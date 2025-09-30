import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss
import os
import pickle
import requests
from flask import Flask, request, jsonify
from rapidfuzz import process
import re
import unidecode
import traceback
import json
import threading
import asyncio
import concurrent.futures



# -----------------------
# CONFIGURACIÓN
# -----------------------
DATASET_FILE = "dataset_fusionado_final_8.csv"
MODEL_NAME = "all-MiniLM-L6-v2"

TMDB_API_KEY = "Tu APIkey"
GOOGLE_API_KEY = "Tu APIkey"
RAWG_API_KEY = "Tu APIkey"
POSTER_BASE_URL = "https://image.tmdb.org/t/p/w500"

# Variables globales para índice/metadata cargada una única vez
INDICES_GLOBALES = {}
METADATA_GLOBAL = {}


# -----------------------
# FUNCIONES GLOBALES
# -----------------------

# Para reforzar la calidad de los resultados 

PALABRAS_CLAVE_ESPECIAL = {
    # Temas / géneros
    "space": [
        "space", "galaxy", "universe", "planet", "alien", "astronaut", "nasa", "cosmos", "space station",
        "black hole", "wormhole", "spaceship", "extraterrestrial", "solar system", "stars", "orbit",
        "cosmic", "meteor", "asteroid", "comet", "gravity", "moon", "science fiction",
        # Sin tilde y plurales en español
        "espacio", "espacios", "planeta", "planetas", "galaxia", "galaxias", "astronauta", "astronautas",
        "extraterrestre", "extraterrestres", "nave espacial", "agujero negro",
        "cosmos", "sistema solar", "estrellas", "órbita", "orbita", "gravedad", "luna", "lunas", "viaje espacial"
    ],

    "adventure": [
        "adventure", "journey", "expedition", "explorer", "exploration", "quest", "treasure", "voyage",
        "danger", "wilderness", "island", "survival", "map", "discover", "legend", "cave", "jungle",
        "hunt", "odyssey",
        # Español variantes, plurales y sin tilde
        "aventura", "aventuras", "viaje", "viajes", "expedición", "expediciones", "explorador", "exploradores",
        "exploración", "exploraciones", "busqueda", "búsqueda", "busquedas", "búsquedas",
        "tesoro", "tesoros", "travesía", "travesias", "peligro", "peligros", "selva", "selvas",
        "desierto", "desiertos", "isla", "islas", "misterio", "misterios", "supervivencia", "descubrimiento",
        "descubrimientos", "río", "rios"
    ],

    "science fiction": [
        "science fiction", "sci-fi", "robot", "android", "ai", "artificial intelligence", "future",
        "time travel", "alien", "cyberpunk", "dystopia", "utopia", "clone", "mutation", "spaceship",
        "technology", "cyborg", "apocalypse", "extraterrestrial", "parallel universe", "space",
        "virtual reality", "computer",
        # Español variantes
        "ciencia ficcion", "ciencia ficción", "ciencia ficcion", "futurista", "robot", "androide",
        "inteligencia artificial", "viaje en el tiempo", "tecnologia", "tecnología", "apocalipsis",
        "mutante", "clon", "ciberpunk", "distopia", "distopía", "nave espacial",
        "futuro", "extraterrestre", "universo paralelo", "realidad virtual"
    ],

    "fantasy": [
        "fantasy", "magic", "wizard", "dragon", "castle", "castles", "elf", "dwarf", "spell",
        "witch", "sorcerer", "sword", "curse", "enchanted", "myth", "legend", "prophecy", "kingdom",
        "creature", "fairy",
        # Español variantes
        "fantasia", "fantasía", "magia", "mago", "magos", "hechizo", "hechizos", "encantamiento",
        "encantamientos", "dragon", "dragón", "castillo", "castillos", "elfo", "elfos", "hada", "hadas",
        "espada", "espadas", "profecia", "profecía", "reino", "reinos", "bruja", "brujas",
        "hechicero", "hechiceros", "maleficio", "maleficios", "mito", "mitos", "leyenda", "leyendas"
    ],

    "horror": [
        "horror", "killer", "ghost", "supernatural", "haunted", "possession", "demon", "vampire",
        "undead", "zombie", "monster", "slasher", "blood", "gore", "nightmare", "paranormal", "asylum",
        "curse", "exorcism", "insanity", "psychopath",
        # Español variantes
        "terror", "miedo", "asesino", "psicopata", "psicópata", "fantasma", "fantasmas", "posesion",
        "posesión", "endemoniado", "demonio", "demonios", "vampiro", "vampiros", "zombi", "zombis",
        "monstruo", "monstruos", "sangre", "gore", "pesadilla", "pesadillas", "paranormal",
        "maleficio", "maleficios", "maldicion", "maldición", "manicomio", "exorcismo"
    ],

    "crime": [
        "crime", "mafia", "gangster", "police", "detective", "corruption", "murder", "investigation",
        "criminal", "heist", "robbery", "theft", "lawyer", "court", "trial", "witness", "drug", "homicide",
        "forensic",
        # Español variantes
        "crimen", "delito", "mafia", "pandillero", "pandilleros", "policia", "policía", "detective",
        "corrupcion", "corrupción", "asesinato", "investigacion", "investigación", "criminal", "robo",
        "atraco", "abogado", "tribunal", "juicio", "testigo", "drogas", "homicidio", "forense"
    ],

    "drama": [
        "drama", "emotional", "tragedy", "conflict", "relationship", "family", "friendship", "love",
        # Español variantes
        "drama", "emocional", "tragedia", "conflicto", "relacion", "relación", "familia", "amistad",
        "amor", "superacion", "superación"
    ],

    "romance": [
        "romance", "love", "relationship", "passion", "affair", "crush", "wedding", "lover", "date",
        "heartbreak", "marriage", "jealousy", "forbidden love",
        # Español variantes
        "romantico", "romántico", "romance", "relacion", "relación", "amor", "pasion", "pasión",
        "amante", "matrimonio", "boda", "noviazgo", "celos", "ruptura", "pareja"
    ],

    "animation": [
        "animation", "cartoon", "animated", "cgi", "3d animation", "stop motion", "family", "children",
        "pixar", "disney", "anime",
        # Español variantes
        "animacion", "animación", "dibujo animado", "caricatura", "3d", "stop motion", "infantil", "familiar"
    ],

    "superhero": [
        "superhero", "powers", "comic", "mutant", "marvel", "dc", "villain", "secret identity", "city",
        "mask", "cape", "rescue", "universe", "league", "vigilante", "hero", "sidekick", "costume", "mutation",
        # Español variantes
        "superheroe", "superhéroe", "poderes", "comic", "cómic", "universo", "villano", "justiciero",
        "identidad secreta", "ciudad", "mascara", "máscara", "traje", "rescate", "héroe", "compañero",
        "capa", "mutacion", "mutación"
    ],

    "time travel": ["time travel", "temporal", "future", "past", "timeline", "chronology"],

    "marvel": [
    "marvel", "avengers", "capitan america", "asgard", "thor", "loki", "iron man", "ironman", "captain america",
    "black widow", "hulk", "black panther", "spiderman", "spider-man", "doctor strange", "strange",
    "ant-man", "antman", "wasp", "hawkeye", "scarlet witch", "vision", "falcon", "winter soldier",
    "guardians of the galaxy", "gamora", "drax", "rocket raccoon", "groot", "star-lord",
    "nick fury", "shuri", "wanda maximoff", "peter parker", "tony stark", "bruce banner",
    "clint barton", "natasha romanoff", "steve rogers", "sam wilson", "bucky barnes",
    "iron patriot", "marvel cinematic universe", "mcu", "infinity stones", "thanos", "galactus",
    "x-men", "magneto", "wolverine", "deadpool", "silver surfer", "doctor doom",
    "sokovia", "avengers tower", "stark industries", "shield", "hydra", "ultron", "hellfire club",
    "new york", "quantum realm", "time stone", "space stone", "reality stone",
    "mantis", "hela", "blade", "spider-man no way home",
    "black widow", "wanda", "nick fury", "samuel l jackson"
    ],

    "war": [
        "war", "soldier", "battle", "army", "military", "conflict", "front", "combat", "troop",
        "strategy", "invasion", "weapon", "victory", "defeat", "prisoner",
        # Español variantes
        "guerra", "soldado", "batalla", "ejercito", "ejército", "militar", "combate", "frente", "invasion",
        "invasión", "arma", "estrategia", "prisionero", "victoria", "derrota"
    ],

    "sports": [
        "sport", "team", "match", "championship", "athlete", "coach", "goal", "tournament", "score",
        "player", "win", "competition", "training", "football", "basketball", "baseball", "olympics",
        # Español variantes
        "deporte", "equipo", "partido", "campeonato", "atleta", "entrenador", "gol", "torneo",
        "jugador", "victoria", "competicion", "competición", "entrenamiento", "futbol", "fútbol", "baloncesto",
        "beisbol", "béisbol", "olimpiadas"
    ],

    "thriller": [
        "thriller", "suspense", "mystery", "danger", "conspiracy", "crime", "detective", "psychological",
        "investigation", "tension", "fear", "enemy", "twist",
        # Español variantes
        "suspense", "misterio", "peligro", "conspiracion", "conspiración", "crimen", "detective",
        "psicologico", "psicológico", "investigacion", "investigación", "tension", "tensión",
        "enemigo", "giro"
    ],




    # Sagas populares o franquicias, con títulos clave para filtro específico
    "marvel": [
        "iron man", "the avengers", "captain america: the first avenger", "thor", "guardians of the galaxy",
        "black panther", "doctor strange", "spider-man: homecoming", "avengers: infinity war",
        "avengers: endgame",
        # Agrega más títulos si deseas
    ],

    "harry_potter": [
        "harry potter and the sorcerer's stone", "harry potter and the chamber of secrets",
        "harry potter and the prisoner of azkaban", "harry potter and the goblet of fire",
        "harry potter and the order of the phoenix", "harry potter and the half-blood prince",
        "harry potter and the deathly hallows - part 1", "harry potter and the deathly hallows - part 2",
        "fantastic beasts and where to find them", "fantastic beasts: the crimes of grindelwald"
    ],

    "the_lord_of_the_rings": [
        "the fellowship of the ring", "the two towers", "the return of the king",
        "the hobbit: an unexpected journey", "the hobbit: the desolation of smaug",
        "the hobbit: the battle of the five armies"
    ],

    "star_wars": [
        "star wars: episode i – the phantom menace", "star wars: episode ii – attack of the clones",
        "star wars: episode iii – revenge of the sith", "star wars: episode iv – a new hope",
        "star wars: episode v – the empire strikes back", "star wars: episode vi – return of the jedi",
        "star wars: episode vii – the force awakens", "star wars: episode viii – the last jedi",
        "star wars: episode ix – the rise of skywalker"
    ],

    "game_of_thrones": [
        "game of thrones - season 1", "game of thrones - season 2", "game of thrones - season 3",
        "game of thrones - season 4", "game of thrones - season 5", "game of thrones - season 6",
        "game of thrones - season 7", "game of thrones - season 8"
    ],

    "pokemon": [
        "pokemon red", "pokemon blue", "pokemon yellow", "pokemon gold", "pokemon silver",
        "pokemon ruby", "pokemon sapphire", "pokemon diamond", "pokemon pearl", "pokemon black",
        "pokemon white", "pokemon sword", "pokemon shield", "pokemon go"
    ],
     # SAGA TIBURÓN / JAWS
    "jaws": [
        "jaws", "tiburón", "tiburon", "steven spielberg", "megalodon", "shark", "shark attack", "orca", 
        "amity island", "deep blue sea", "48 meters", "open water", "tiburones"
    ],
    # JURASSIC PARK / WORLD
    "jurassic_park": [
        "jurassic park", "parque jurásico", "john hammond", "ian malcolm", "alan grant", "ellie sattler",
        "jurassic world", "isla nublar", "dinosaur", "velociraptor", "t-rex", "dinosurio", "tyrannosaurus",
        "mosasaurio"
    ],
    # PIRATAS DEL CARIBE
    "pirates_of_the_caribbean": [
        "pirates of the caribbean", "piratas del caribe", "jack sparrow", "will turner",
        "elizabeth swann", "black pearl", "davy jones", "salazar", "barbossa", "kraken", "pirate"
    ],
    # INDIANA JONES
    "indiana_jones": [
        "indiana jones", "indy", "henry jones", "raiders of the lost ark", "temple of doom",
        "last crusade", "crystal skull", "ark of the covenant", "nazis", "whip", "fedor", "arca perdida"
    ],
    # JAMES BOND / 007
    "james_bond": [
        "james bond", "007", "mi6", "m", "q", "martini", "goldfinger", "skyfall", "spectre",
        "casino royale", "dr no", "license to kill", "bond girl", "jaws (villain)", "octopussy"
    ],
    # FAST AND FURIOUS
    "fast_and_furious": [
        "fast and furious", "rápidos y furiosos", "dom toretto", "paul walker", "racing", "furious",
        "fast five", "tokyo drift", "hobbs", "crew", "street race", "nitro"
    ],
    # TWILIGHT - CREPÚSCULO
    "twilight": [
        "twilight", "crepúsculo", "bella swan", "edward cullen", "jacob black", "vampiro", "werewolf",
        "luna nueva", "amanecer", "eclipse", "breaking dawn"
    ],
    # MATRIX
    "matrix": [
        "matrix", "neo", "morpheus", "trinity", "mr. anderson", "agente smith", "zion", "red pill",
        "blue pill", "oracle", "revolutions", "recargado", "the matrix", "machines", "simulación"
    ],
    # TERMINATOR
    "terminator": [
        "terminator", "t-800", "skynet", "john connor", "sarah connor", "liquid metal", 
        "machine", "cyborg", "i'll be back", "judgment day"
    ],
    # ROCKY / CREED
    "rocky": [
        "rocky", "balboa", "apollo creed", "ivan drago", "clubber lang", "paulie", "boxeo", "boxing",
        "philadelphia", "creed", "adrian"
    ],
    # MISSION IMPOSSIBLE
    "mission_impossible": [
        "mission impossible", "ethan hunt", "imf", "impossible mission force", "tom cruise",
        "ghost protocol", "rogue nation", "fallout", "protocolo fantasma"
    ],
    # SAGAS DE CARRERAS (Coches y competición automovilística)
"racing_saga": [
    "carrera", "carreras", "racing", "competition", "competición", "coches", "coche", "auto", "autos",
    "car", "cars", "vehículo", "vehículos", "vehiculo", "vehiculos",
    "automovil", "automóviles", "automovilismo", "motorsport", "piloto", "pilotos",
    "pista", "pistas", "circuito", "circuitos", "gran premio", "grand prix", "f1", "fórmula 1", "formula 1",
    "rally", "monoplaza", "kart", "karting", "turismo", 
    "pole position", "parrilla de salida", "podio", "finish", "meta", "pit stop", "velocidad", "drift", "derrape",
    "box", "boxes", "vuelta rápida", "vuelta de formación", "simulador de carreras", "campeonato", "motor", "deportivo",
    "nascar", "indicar", "drag", "resistencia", "maratón automovilístico",
    # Títulos y sagas famosas:
    "gran turismo", "fast and furious", "rápidos y furiosos", "rush", "need for speed", "days of thunder",
    "cars", "senna", "ford v ferrari", "le mans", "fórmula", "speed racer"
    ],
    
    "the_witcher": [
            "the witcher", "geralt", "yennefer", "cirilla", "monster hunter", "kaer morhen"
        ],

    "breaking_bad": [
        "breaking bad", "walter white", "jesse pinkman", "heisenberg", "meth", "drug"
    ],

    "stranger_things": [
        "stranger things", "upside down", "eleven", "demogorgon", "hawkins"
    ],

    "rick_and_morty": [
        "rick and morty", "rick sanchez", "morty smith", "portal gun", "multiverse"
    ],

    "vikings": [
        "vikings", "ragnar lothbrok", "lagertha", "floki", "kattegat"
    ],

    "star_trek": [
        "star trek", "enterprise", "captain kirk", "spock", "vulcan", "klingon"
    ],

    "harry_potter_books": [
        "harry potter and the sorcerer's stone", "harry potter and the chamber of secrets",
        "harry potter and the prisoner of azkaban", "harry potter and the goblet of fire",
        "harry potter and the order of the phoenix", "harry potter and the half-blood prince",
        "harry potter and the deathly hallows"
    ],

    "lord_of_the_rings_books": [
        "the fellowship of the ring", "the two towers", "the return of the king",
        "the hobbit"
    ],

    "elden_ring": [
        "elden ring", "ashen one", "limgrave", "radagon", "the two fingers"
    ],

    "call_of_duty": [
        "call of duty", "mw", "modern warfare", "black ops", "zombies", "warzone"
    ],

    "minecraft": [
        "minecraft", "voxel", "block", "creeper", "enderman", "nether"
    ],

    "fortnite": [
        "fortnite", "battle royale", "epic games", "building", "skins"
    ],

    "league_of_legends": [
        "league of legends", "lol", "summoner", "champion", "nexus", "riot games"
    ],
    "el_exorcista": [
        "el exorcista", "regan macneil", "pazuzu", "exorcismo", "poseída", "padre merrin",
        "demonio", "terror", "horror", "la cruz invertida"
    ],
    # HALLOWEEN
    "halloween": [
        "halloween", "michael myers", "jamie lee curtis", "masacre", "slasher",
        "haddonfield", "máscara blanca", "ladder", "knife", "halloween night"
    ],
    # PESADILLA EN ELM STREET (Nightmare on Elm Street)
    "pesadilla_en_elm_street": [
        "freddy krueger", "pesadilla en elm street", "elm street", "dream killer",
        "máscara de quemaduras", "guantes con cuchillas", "slasher", "terror"
    ],
    # SAW
    "saw": [
        "saw", "jigsaw", "juego macabro", "trap", "puzzle", "rompecabezas", "puzzle mortal",
        "slasher", "terror psicológico"
    ],
    # IT (ESO)
    "it": [
        "it", "eso", "pennywise", "payaso", "clown", "derry", "horror", "terror",
        "globos rojos", "club de los perdedores"
    ],
    # THE CONJURING (El conjuro)
    "the_conjuring": [
        "el conjuro", "the conjuring", "ed y lorretta warren", "caso", "espiritu",
        "poseído", "terror", "horror", "demoniaco"
    ],
    # THE RING (La señal)
    "the_ring": [
        "the ring", "la señal", "video maldito", "samara", "terror", "horror",
        "pozo", "fatal"
    ],
    # TEXAS CHAINSAW MASSACRE (La matanza de Texas)
    "texas_chainsaw_massacre": [
        "texas chainsaw massacre", "la masacre de texas", "leatherface",
        "motosierra", "slasher", "familia caníbal", "horror", "terror"
    ],
    # ANNABELLE
    "annabelle": [
        "annabelle", "muñeca poseída", "horror", "terror", "demonio",
        "conjuro", "the conjuring"
    ],
    # INSIDIOUS
    "insidious": [
        "insidious", "espíritus", "terror", "horror", "paranormal", "possession",
        "más allá", "la dimensión oscura"
    ],
    # CHILD'S PLAY / CHUCKY
    "childs_play": [
        "chucky", "child's play", "muñeco diabólico", "terror", "slasher",
        "muñeca asesina", "brad dourif", "serial killer"
    ],
    # THE WENDIGO
    "the_wendigo": [
        "wendigo", "leyenda", "monstruo", "terror sobrenatural", "cannibalismo", "bosque",
        "espíritu maligno"
    ],
    # EL ARO
    "el_aro": [
        "el aro", "la señal", "vídeo maldito", "samara", "terror", "horror",
        "pozo", "fatal"
    ],
    # THE BLAIR WITCH PROJECT
    "blair_witch_project": [
        "blair witch project", "brujas", "bosque", "terror psicológico",
        "documental falso", "found footage", "exploradores"
    ],
    # PET SEMATARY (Cementerio de animales)
    "pet_sematary": [
        "pet sematary", "cementerio de animales", "resurrección", "terror",
        "horror", "stephen king"
    ]

}

GENEROS_FORZADOS = {
    "jaws": ["thriller", "horror", "adventure"],
    "el señor de los anillos": ["fantasy", "adventure"],
    "the lord of the rings": ["fantasy", "adventure"],
    "pokemon": ["animation", "adventure", "fantasy", "family"],
    "harry potter": ["fantasy", "adventure", "family"],
    "star wars": ["science fiction", "adventure"],
    "game of thrones": ["fantasy", "drama"],
    "jurassic park": ["science fiction", "adventure"],
    "marvel": ["superhero", "action", "adventure"],
    "pirates of the caribbean": ["adventure", "fantasy"],
    "the matrix": ["science fiction", "action"],
    "fast and furious": ["action", "crime"],
    "twilight": ["romance", "fantasy"],
    "indiana jones": ["adventure", "action"],
    "james bond": ["action", "thriller"],
    "ironman": ["superhero", "action", "adventure"],
    "loki": ["superhero", "marvel", "fantasy", "time travel"],
    "capitan america": ["superhero", "action", "adventure"],
     "el exorcista": ["horror", "thriller", "supernatural"],
    "the exorcist": ["horror", "thriller", "supernatural"],
    "it": ["horror", "thriller", "supernatural"],
    "eso": ["horror", "thriller", "supernatural"],  
    "pennywise": ["horror", "thriller", "supernatural"],
    "hellraiser": ["horror", "supernatural", "thriller"],
    "scream": ["horror", "slasher", "thriller"],
    "nightmare on elm street": ["horror", "slasher", "thriller"],
    "pesadilla en elm street": ["horror", "slasher", "thriller"],
    "freddy krueger": ["horror", "slasher", "thriller"],
    "halloween": ["horror", "slasher", "thriller"],
    "michael myers": ["horror", "slasher", "thriller"],
    "the shining": ["horror", "psychological", "thriller"],
    "el resplandor": ["horror", "psychological", "thriller"],
    "the ring": ["horror", "supernatural", "thriller"],
    "el aro": ["horror", "supernatural", "thriller"],
    "annabelle": ["horror", "supernatural", "thriller"],
    "the conjuring": ["horror", "supernatural", "thriller"],
    "it follows": ["horror", "thriller", "supernatural"],
    "sinister": ["horror", "supernatural", "thriller"],
    "pyramid": ["horror", "mystery", "thriller"],
    "insidious": ["horror", "supernatural", "thriller"],
    "poltergeist": ["horror", "supernatural"],
    "candyman": ["horror", "thriller"],
    "the wolfman": ["horror", "supernatural"],
    "dracula": ["horror", "supernatural"],
    "frankenstein": ["horror", "classic"],
    "the texas chainsaw massacre": ["horror", "slasher"],
    "leatherface": ["horror", "slasher"],
    "pet sematary": ["horror", "thriller", "supernatural"],
    "the blair witch project": ["horror", "found footage", "thriller"],
    "inception": ["science fiction", "thriller", "action"],
    "interstellar": ["science fiction", "drama", "adventure"],
    "avengers": ["superhero", "action", "adventure"],
    "the dark knight": ["action", "crime", "drama"],
    "logan": ["superhero", "drama", "action"],
    "deadpool": ["superhero", "action", "comedy"],
    "the lion king": ["animation", "family", "adventure"],
    "frozen": ["animation", "family", "fantasy"],
    "toy story": ["animation", "family", "comedy"],
    "the godfather": ["crime", "drama"],
    "the shawshank redemption": ["drama", "crime"],
    "parasite": ["thriller", "drama", "mystery"],
    "joker": ["drama", "crime", "thriller"],
    "black panther": ["superhero", "action", "adventure"],
    "star trek": ["science fiction", "adventure"],
    "guardians of the galaxy": ["superhero", "action", "comedy"],
    "deadpool 2": ["superhero", "action", "comedy"],
    "mad max": ["action", "adventure", "science fiction"],
    "the hunger games": ["action", "adventure", "drama"],
    "wonder woman": ["superhero", "action", "adventure"],
    "thor": ["superhero", "action", "adventure"],
    "doctor strange": ["superhero", "action", "fantasy"],
    "the hobbit": ["fantasy", "adventure"],
    "avatar": ["science fiction", "action", "adventure"],
    "black widow": ["superhero", "action", "thriller"],
    "matrix revolutions": ["science fiction", "action"],
    "gran turismo": ["sports", "action", "adventure", "video game"],
    "the witcher": ["fantasy", "adventure", "drama"],
    "breaking bad": ["crime", "drama", "thriller"],
    "stranger things": ["science fiction", "horror", "drama"],
    "friends": ["comedy", "romance"],
    "the office": ["comedy"],
    "narcos": ["crime", "drama", "thriller"],
    "black mirror": ["science fiction", "drama", "thriller"],
    "the mandalorian": ["science fiction", "adventure", "fantasy"],
    "rick and morty": ["animation", "comedy", "science fiction"],
    "vikings": ["action", "drama", "history"],
    "house of cards": ["drama", "thriller"],
    "westworld": ["science fiction", "drama", "thriller"],
    "the crown": ["drama", "history"],
    "the flash": ["superhero", "action", "adventure"],
    "daredevil": ["superhero", "action", "drama"],
    "sherlock": ["crime", "drama", "mystery"],
    "peaky blinders": ["crime", "drama", "history"],
    "the walking dead": ["horror", "drama", "thriller"],
    "lucifer": ["drama", "crime", "fantasy"],
    "the big bang theory": ["comedy"],
    "how i met your mother": ["comedy", "romance"],
    "game of thrones books": ["fantasy", "adventure", "drama"],
    "lord of the rings books": ["fantasy", "adventure"],
    "harry potter books": ["fantasy", "adventure", "family"],
    "elden ring": ["role-playing", "fantasy", "action"],
    "the last of us": ["action", "adventure", "drama"],
    "cyberpunk 2077": ["action", "role-playing", "science fiction"],
    "witcher 3": ["role-playing", "fantasy", "adventure"],
    "minecraft": ["sandbox", "survival", "crafting"],
    "fortnite": ["battle royale", "shooter", "multiplayer"],
    "call of duty": ["shooter", "action", "multiplayer"],
    "tomb raider": ["action", "adventure", "platformer", "puzzle", "exploration"],
    "elden ring": ["role-playing", "fantasy", "action", "open world"],
    "call of duty": ["shooter", "action", "multiplayer", "war"],
    "minecraft": ["sandbox", "survival", "crafting", "open world"],
    "fortnite": ["battle royale", "shooter", "multiplayer", "building"],
    "league of legends": ["multiplayer", "battle arena", "strategy", "competitive"],
    "cyberpunk 2077": ["role-playing", "science fiction", "open world", "action"],
    "witcher 3": ["role-playing", "fantasy", "adventure", "open world"],
    "god of war": ["action", "adventure", "mythology", "combat"],
    "assassin's creed": ["action", "adventure", "stealth", "historical"],
    "dark souls": ["role-playing", "fantasy", "difficult", "action"],
    "final fantasy": ["role-playing", "fantasy", "turn-based", "story rich"],
    "super mario": ["platformer", "adventure", "family", "classic"],
    "halo": ["shooter", "science fiction", "multiplayer", "space"],
    "the last of us": ["action", "adventure", "survival", "story driven"],
}



COMBINACIONES_PROHIBIDAS = [
    {"horror", "family"},
    {"horror", "animation"},
    {"horror", "comedy"},
    {"horror", "familiar"},
    {"horror", "animación"},
    {"terror", "familiar"},
    {"terror", "animación"},
    {"thriller", "animation"},
    {"thriller", "familiar"},
    {"comedy", "war"},
    {"comedy", "crime"},      
    {"romance", "horror"},
    {"romance", "thriller"},   
    {"romance", "terror"},
    {"children", "horror"},      
    {"children", "thriller"},
    {"documentary", "fantasy"}, 
    {"superhero", "documentary"},
    {"sports", "horror"},
    {"sports", "fantasy"},
    {"musical", "horror"},
    {"musical", "war"},
    {"musical", "crime"},
    {"adult", "family"},
    {"adult", "children"},
    {"family", "crime"},
    {"family", "thriller"},
    {"family", "war"},
]



tipo_pesos = {"pelicula": 1.0, "serie": 0.95, "libro": 0.8, "videojuego": 0.9}

traducciones = {
    "terror": "horror", "romance": "romance", "acción": "action", "aventura": "adventure",
    "ciencia ficción": "science fiction", "comedia": "comedy", "drama": "drama", "misterio": "mystery",
    "fantasía": "fantasy", "historia": "history", "documental": "documentary", "crimen": "crime",
    "familia": "family", "animación": "animation", "musical": "music", "bélico": "war", "western": "western",
    "sci-fi": "science fiction", "space": "science fiction", "thriller": "mystery", "adulto": "adult",

}



# -----------------------
# CARGAR DATASET
# -----------------------
def cargar_dataset():
    print("... Cargando dataset...")
    df = pd.read_csv(DATASET_FILE, low_memory=False)

    if "tipo" not in df.columns:
        raise ValueError("El dataset debe tener la columna 'tipo'.")

    def seleccionar_descripcion(row):
        if row["tipo"] == "pelicula":
            return row.get("overview", "")
        else:
            return row.get("descripcion_castellano", "")

    df["overview"] = df.apply(seleccionar_descripcion, axis=1).fillna("")
    return df

df = cargar_dataset()
model = SentenceTransformer(MODEL_NAME)


# -----------------------
# CARGAR O CREAR ÍNDICE
# -----------------------
def crear_o_cargar_indice(tipo_filtrado):
    tipos_validos = ['pelicula', 'serie', 'libro', 'videojuego']
    if tipo_filtrado not in tipos_validos:
        print(f"Tipo inválido: '{tipo_filtrado}'. Debe ser uno de {tipos_validos}.")
        return None, None

    index_file = f"{tipo_filtrado}.index"
    metadata_file = f"{tipo_filtrado}_metadata.pkl"

    # Intentar cargar índice y metadatos ya existentes
    if os.path.exists(index_file) and os.path.exists(metadata_file):
        print(f"Cargando índice FAISS existente para tipo '{tipo_filtrado}'...")
        try:
            index = faiss.read_index(index_file)
            with open(metadata_file, "rb") as f:
                media_metadata = pickle.load(f)
            return index, media_metadata
        except Exception as e:
            print(f"Error al cargar el índice o metadatos: {e}")
            return None, None

    # Si no existen, crear embeddings y FAISS index
    print(f"Creando embeddings y FAISS index para tipo '{tipo_filtrado}'...")

    df_filtrado = df[df["tipo"].str.lower() == tipo_filtrado]
    if df_filtrado.empty:
        print(f"No hay datos del tipo '{tipo_filtrado}' en el dataset.")
        return None, None

    textos = df_filtrado["overview"].fillna("").tolist()

    try:
        # Generar embeddings
        embeddings = model.encode(textos, batch_size=64, show_progress_bar=True)
        embeddings = np.array(embeddings, dtype="float32")

        # Normalizar para similitud coseno (producto interno)
        faiss.normalize_L2(embeddings)

        # Crear índice FAISS
        dimension = embeddings.shape[1]
        index = faiss.IndexFlatIP(dimension)
        index.add(embeddings)

        # Guardar índice y metadatos
        faiss.write_index(index, index_file)

        media_metadata = df_filtrado.to_dict(orient="records")
        with open(metadata_file, "wb") as f:
            pickle.dump(media_metadata, f)

        print(f"Índice creado con {len(media_metadata)} elementos.")
        return index, media_metadata

    except Exception as e:
        print(f"Error al crear índice FAISS: {e}")
        return None, None





# -----------------------
# FUNCIONES AUXILIARES
# -----------------------

# --- Cache para info externa ---
api_cache = {}

def obtener_info_externa_cache(tipo, titulo):
    key = (tipo, titulo.lower().strip())
    if key in api_cache:
        return api_cache[key]
    info = None
    try:
        if tipo == "pelicula":
            info = obtener_info_pelicula_tmdb(titulo)
        elif tipo == "serie":
            info = obtener_info_serie_tmdb(titulo)
        elif tipo == "libro":
            info = buscar_libro_google(titulo)
        elif tipo == "videojuego":
            info = buscar_videojuego_rawg(titulo)
    except Exception as e:
        print(f"Error obteniendo info externa tipo={tipo} titulo={titulo}: {e}")
        traceback.print_exc()
        info = None
    api_cache[key] = info
    return info


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
        print(f"NO se encontraron datos válidos para '{titulo}' en TMDb.")
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

            detalles = obtener_info_pelicula_tmdb(titulo)
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
        print(f"Error al buscar libro: {e}")

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
        print("Error al hacer la búsqueda en Google Books.")
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











# -------------------------------------------------------------------------------------------------------
# BÚSQUEDA PRINCIPAL
# -------------------------------------------------------------------------------------------------------


# ---------------- FUNCIONES AUXILIARES --------------------

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
        print(f"Error API externa [{tipo}]: '{titulo}': {e}")
        traceback.print_exc()
        result = None
    api_cache[key] = result
    return result


def normalizar_titulo(titulo):
    if not isinstance(titulo, str):
        return ""
    return unidecode.unidecode(titulo.lower().strip())




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


def mapear_genero(g):
    if not isinstance(g, str):
        return ""
    return traducciones.get(g.lower(), g.lower())


def parsear_generos(generos_raw, mapear=mapear_genero):
    if not generos_raw:
        return []
    try:
        # Para prevenir errores o strings vacíos
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
        print(f"Error parseando géneros: {e}")
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


def boost_score(score, genero_compartido, generos_busqueda, item_genres):
    if genero_compartido:
        bonus = 1.2
        if generos_busqueda and item_genres and generos_busqueda[0] == item_genres[0]:
            bonus += 0.20
    else:
        bonus = 0.8
    return score * bonus







lock_indices = threading.Lock()

def get_index_and_metadata(tipo_destino):
    with lock_indices:
        if tipo_destino not in INDICES_GLOBALES or tipo_destino not in METADATA_GLOBAL:
            index, metadata = crear_o_cargar_indice(tipo_destino)
            INDICES_GLOBALES[tipo_destino] = index
            METADATA_GLOBAL[tipo_destino] = metadata
        return INDICES_GLOBALES[tipo_destino], METADATA_GLOBAL[tipo_destino]

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
    print(f"🔍 Buscando en dataset: '{query}' (intento {intentos + 1})")
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

                        print(f"\n✅ Recomendaciones para tipo '{t}':", flush=True)
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
        print( "No se pudo cargar o crear índice.")
        return []

    info = obtener_info_externa_cache(tipo_origen, query)
    generos_forzados = GENEROS_FORZADOS.get(titulo_norm)
    generos_busqueda = []
    query_text = query
    if generos_forzados:
        print(f"Usando géneros forzados para '{query}': {generos_forzados}")
        generos_busqueda = generos_forzados
    else:
        if info and isinstance(info, dict):
            if info.get("generos") and isinstance(info["generos"], list):
                generos_busqueda = [g.lower() for g in info["generos"][:3]]
                print(f"Géneros extraídos: {generos_busqueda}")
            if info.get("descripcion"):
                query_text = info["descripcion"]
                print("Usando descripción para embedding")

    if genero:
        generos_busqueda.append(mapear_genero(genero))

    generos_busqueda = list(dict.fromkeys([mapear_genero(g) for g in generos_busqueda]))
    if "documentary" in generos_busqueda or tipo_dest_busqueda == "videojuego":
        generos_busqueda = []
    print(f"🔄 Géneros finales: {generos_busqueda}")

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
                            print(f"Rechazado por filtro palabras clave y sin género/puntuación suficiente: {titulo}")
                            continue
                        else:
                            print(f"No cumple palabras clave pero pasa por género/puntuación: {titulo}")
            else:
                print(f"Descripción corta o vacía: {titulo}")

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


# -----------------------
# API FLASK
# -----------------------

app = Flask(__name__)

@app.route("/recomendar", methods=["POST"])
def recomendar():
    data = request.json
    query = data.get("query")
    tipo_origen = data.get("tipo_origen", "pelicula")
    tipo_destino = data.get("tipo_destino", "pelicula")
    genero = data.get("genero")
    top_k = int(data.get("top_k", 5))

    # Normalizamos tipo_origen y tipo_destino para evitar errores por mayúsculas
    if isinstance(tipo_origen, str):
        tipo_origen = tipo_origen.lower()
    else:
        tipo_origen = "pelicula"

    if isinstance(tipo_destino, str):
        tipo_destino = tipo_destino.lower()
    elif isinstance(tipo_destino, list):
        tipo_destino = [t.lower() for t in tipo_destino]
    else:
        tipo_destino = "pelicula"  # Valor por defecto seguro

    if not query or not tipo_origen:
        return jsonify({"error": "Faltan parámetros obligatorios: 'query' y 'tipo_origen'"}), 400

    recomendaciones = buscar_recomendaciones(
        query, 
        tipo_origen=tipo_origen, 
        tipo_destino=tipo_destino, 
        top_k=top_k, 
        genero=genero
    )

    if not recomendaciones:
        return jsonify({"mensaje": "No se encontraron recomendaciones."}), 404

    return jsonify({"recomendaciones": recomendaciones})



# -----------------------
# EJECUCIÓN LOCAL
# -----------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
