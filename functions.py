from transformers import pipeline
import requests
import json

classifier = pipeline(
    task="text-classification",
    model="joeddav/distilbert-base-uncased-go-emotions-student",
    top_k=None
)

MAPEO_BIG_FIVE = {
    "Apertura a la experiencia":  ["admiration", "amusement", "curiosity", "desire", "excitement", "joy", "nervousness", "optimism"],
    "Responsabilidad": ["approval", "remorse", "caring",  "gratitude", "determination", "satisfaction", "pride", "realization"],
    "Extroversión":["curiosity", "excitement", "optimism", "joy", "pride", "admiration", "amusement"],
    "Amabilidad": ["desire", "caring", "optimism", "neutral", "approval", "gratitude", "love", "admiration"],
    "Neuroticismo": ["embarrassment", "remorse", "confusion", "anxiety", "annoyance", "fear", "anger", "disgust"]
}

def translate_text(text, dest='en', src='auto'):
    """Traduce texto usando la API de Google Translate"""
    url = "https://translate.googleapis.com/translate_a/single"
    params = {
        'client': 'gtx',
        'sl': src,
        'tl': dest,
        'dt': 't',
        'q': text
    }
    
    response = requests.get(url, params=params)
    response.raise_for_status()
    
    # Extraer texto traducido y lenguaje detectado
    translated_text = response.json()[0][0][0]
    detected_lang = response.json()[2]  # Código de idioma detectado
    
    
    return translated_text, detected_lang

def puntuar_texto(texto):
    # Traducir a inglés y detectar idioma
    texto_traducido, idioma = translate_text(texto, dest='en')
    
    # Clasificar emociones
    emociones = classifier(texto_traducido)
    emociones_ordenadas = sorted(emociones[0], key=lambda x: x["score"], reverse=True)

    # Traducir emoción top al idioma original
    emocion_top_estandar = emociones_ordenadas[0]["label"]
    emocion_top_traducida, _ = translate_text(emocion_top_estandar, dest=idioma, src='en')

    puntuaciones = {rasgo: 0.0 for rasgo in MAPEO_BIG_FIVE.keys()}
    
    for emocion in emociones_ordenadas:
        for rasgo, emociones_relacionadas in MAPEO_BIG_FIVE.items():
            if emocion["label"] in emociones_relacionadas:
                puntuaciones[rasgo] += emocion["score"]

    return puntuaciones, emocion_top_estandar, emocion_top_traducida

def calcular_media_puntuaciones(diario):
    # Inicializar un diccionario para acumular las puntuaciones por categoría
    acumulador = {rasgo: 0.0 for rasgo in MAPEO_BIG_FIVE.keys()}
    contador = len(diario)  # Número de entradas en el diario

    # Sumar las puntuaciones de cada categoría
    for item in diario:
        for rasgo, puntuacion in item.items():
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

def obtener_descripcion(emocion: str, nivel: int, archivo_json: str = "HackUdc25-backend/emotions.json") -> str:
    
    try:
        # Cargar el archivo JSON
        with open(archivo_json, "r", encoding="utf-8") as file:
            datos = json.load(file)
        
        # Buscar la descripción correspondiente
        for item in datos["emotionsList"]:
            if item["emotion"].strip().lower() == emocion.strip().lower() and item["level"] == nivel:
                return item["description"]
        
        # Si no se encuentra la descripción
        return f"No se encontró una descripción para la emoción '{emocion}' con nivel {nivel}."
    
    except FileNotFoundError:
        return f"El archivo '{archivo_json}' no existe."
    except json.JSONDecodeError:
        return f"Error al decodificar el archivo JSON '{archivo_json}'."
    except Exception as e:
        return f"Error inesperado: {e}"