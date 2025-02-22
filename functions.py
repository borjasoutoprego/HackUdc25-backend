from transformers import pipeline
from googletrans import Translator

translator = Translator()

classifier = pipeline(
    task="text-classification",
    model="joeddav/distilbert-base-uncased-go-emotions-student",
    top_k=None  # Mostrar todas las emociones detectadas
)

MAPEO_BIG_FIVE = {
    "Openness":  ["admiration", "amusement", "curiosity", "desire", "excitement", "joy", "nervousness", "optimism"],
    "Conscientiousness": ["approval", "remorse", "caring",  "gratitude", "determination", "satisfaction", "pride", "realization"],
    "Extraversion":["curiosity", "excitement", "optimism", "joy", "pride", "admiration", "amusement"],
    "Agreeableness": ["desire", "caring", "optimism", "neutral", "approval", "gratitude", "love", "admiration"],
    "Neuroticism": ["embarrassment", "remorse", "confusion", "anxiety", "annoyance", "fear", "anger", "disgust"]
}

def puntuar_texto(texto):
    # Traducir o texto a ingles
    traduccion = translator.translate(texto, dest='en')
    # Almacenamos o idioma no que escribiu o usuario
    idioma = traduccion.src
    # Clasificar as emocions do texto
    emociones = classifier(traduccion.text)
    emociones_ordenadas = sorted(emociones[0], key=lambda x: x["score"], reverse=True)

    emocion_top = emociones_ordenadas[0]
    # Traducimos a emoción máis intensa ao idioma orixinal
    emocion_top["label"] = translator.translate(emocion_top["label"], src='en', dest=idioma).text

    # Calcular as puntuacións dos rasgos de

    puntuaciones = {rasgo: 0.0 for rasgo in MAPEO_BIG_FIVE.keys()}
    
    for emocion in emociones_ordenadas:
        for rasgo, emociones_relacionadas in MAPEO_BIG_FIVE.items():
            if emocion["label"] in emociones_relacionadas:
                puntuaciones[rasgo] += emocion["score"]

    return puntuaciones, emocion_top["label"]

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
            niveles[rasgo] = "MUY ALTO"
        elif media > 0.35:
            niveles[rasgo] = "ALTO"
        elif media > 0.2:
            niveles[rasgo] = "MEDIO"
        elif media > 0.1:
            niveles[rasgo] = "BAJO"
        else:
            niveles[rasgo] = "MUY BAJO"
    return niveles
