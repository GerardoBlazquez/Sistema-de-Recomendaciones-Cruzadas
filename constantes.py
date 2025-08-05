
# -----------------------
# FUNCIONES GLOBALES
# -----------------------

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
    # Puedes añadir tantas sagas/franquicias como desees siguiendo este modelo

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
   
    # Más combinaciones coherentes a evitar:
    {"comedy", "war"},
    {"comedy", "crime"},         # Comedia muy ligera y crimen serio difícil de mezclar
    {"romance", "horror"},
    {"romance", "thriller"},     # Romance y thriller pueden ser conflictivos para recomendación general
    {"romance", "terror"},
    {"children", "horror"},      # Infantil y terror son incompatibles en general
    {"children", "thriller"},
    {"documentary", "fantasy"}, # Documental y fantasía no suelen mezclarse
    {"documentary", "superhero"},
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
    # Más si quieres
}
