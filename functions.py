from transformers import pipeline
from googletrans import Translator

translator = Translator()

classifier = pipeline(
    task="text-classification",
    model="joeddav/distilbert-base-uncased-go-emotions-student",
    top_k=None  # Mostrar todas las emociones detectadas
)

MAPEO_BIG_FIVE = {
    "Apertura a la Experiencia":  ["admiration", "amusement", "curiosity", "desire", "excitement", "joy", "nervousness", "optimism"],
    "Responsabilidad": ["approval", "remorse", "caring",  "gratitude", "determination", "satisfaction", "pride", "realization"],
    "Extroversion":["curiosity", "excitement", "optimism", "joy", "pride", "admiration", "amusement"],
    "Amabilidad": ["desire", "caring", "optimism", "neutral", "approval", "gratitude", "love", "admiration"],
    "Neuroticismo": ["embarrassment", "remorse", "confusion", "anxiety", "annoyance", "fear", "anger", "disgust"]
}

def puntuar_texto(texto):
    # Traducir o texto a ingles
    traduccion = translator.translate(texto, dest='en')
    # Almacenamos o idioma no que escribiu o usuario
    idioma = traduccion.src
    # Clasificar as emocions do texto
    emociones = classifier(traduccion.text)
    emociones_ordenadas = sorted(emociones[0], key=lambda x: x["score"], reverse=True)

    emocion_top_estandar = emociones_ordenadas[0]["label"]
    # Traducimos a emoción máis intensa ao idioma orixinal
    emocion_top = translator.translate(emocion_top_estandar, src='en', dest=idioma).text

    puntuaciones = {rasgo: 0.0 for rasgo in MAPEO_BIG_FIVE.keys()}
    
    for emocion in emociones_ordenadas:
        for rasgo, emociones_relacionadas in MAPEO_BIG_FIVE.items():
            if emocion["label"] in emociones_relacionadas:
                puntuaciones[rasgo] += emocion["score"]

    return puntuaciones, emocion_top_estandar, emocion_top 

def calcular_media_puntuaciones(diario):
    # Inicializar un diccionario para acumular las puntuaciones por categoría
    acumulador = {rasgo: 0.0 for rasgo in MAPEO_BIG_FIVE.keys()}
    contador = len(diario)  # Número de entradas en el diario

    # Sumar las puntuaciones de cada categoría
    for fecha, datos in diario.items():
        puntuaciones_directas = datos["puntuaciones_big_five"]
        for rasgo, puntuacion in puntuaciones_directas.items():
            acumulador[rasgo] += puntuacion

    # Calcular la media de cada categoría
    medias = {rasgo: (acumulador[rasgo] / contador) for rasgo in acumulador}
    return medias

def niveles_personalidad(medias):
    niveles = {}
    for rasgo, media in medias.items():
        if media > 0.45:
            niveles[rasgo] = 4
        elif media > 0.35:
            niveles[rasgo] = 3
        elif media > 0.2:
            niveles[rasgo] = 2
        elif media > 0.1:
            niveles[rasgo] = 1
        else:
            niveles[rasgo] = 0
    return niveles


