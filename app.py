from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from gradio_client import Client
from fastapi import FastAPI, HTTPException, Depends, Header
from sqlalchemy import create_engine, Column, String, ForeignKey, Date, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from jose import jwt, JWTError
from datetime import datetime, timedelta, date
import secrets
import uuid
import json
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Annotated, List
from functions import puntuar_texto, calcular_media_puntuaciones, niveles_personalidad

app = FastAPI()

security = HTTPBearer()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuración de la base de datos
DATABASE_URL = "postgresql://postgres:hackudc@127.0.0.1:5432/hackudc"

# Configuración de seguridad
SECRET_KEY = secrets.token_hex(32)  # Clave secreta para firmar los tokens
ALGORITHM = "HS256"  # Algoritmo de encriptación
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # Tiempo de expiración del token

# Modelo para las credenciales del usuario
class UserCredentials(BaseModel):
    email: str
    password: str

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Modelo de usuario
class User(Base):
    __tablename__ = "users"
    token = Column(String, nullable=True)
    email = Column(String, primary_key=True, index=True)
    password = Column(String)
    

# Modelo del perfil
class Profile(Base):
    __tablename__ = "personal_profile"
    user_email = Column(String, primary_key=True, index=True)
    score_neuroticismo = Column(Float, nullable=False)
    score_extroversión = Column(Float, nullable=False)
    score_agreeableness = Column(Float, nullable=False)
    score_conscientiousness = Column(Float, nullable=False)
    score_openness = Column(Float, nullable=False)

# Crear las tablas
Base.metadata.create_all(bind=engine)

# Dependencia para obtener la sesión de la base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Client de Hugging Face Spaces
client = Client("borjasoutoprego/hackudc25")

# Modelo de datos de entrada
class UserQuery(BaseModel):
    question: str

# Modelo de datos de salida
class AIResponse(BaseModel):
    response: str

class TraitJson(BaseModel):
    trait: str
    score: int
    description: str

# Modelo de salida de la puntuación
class ScoreResponse(BaseModel):
    profile: List[TraitJson]

# Modelo datos de salida del historico del diario
class DiaryJson(BaseModel):
    id: str
    date: date
    text: str
    emotion_estandar: str
    emotion_idioma: str

class HistoryResponse(BaseModel):
    history: List[DiaryJson]

# Modelo de historial de usuario
class UserHistory(Base):
    __tablename__ = "user_history"
    user_email = Column(String, nullable=False)
    interaction = Column(String, nullable=False)
    id_interaction = Column(String, primary_key=True, nullable=False)

# Modelo para la entrada del diario
class DiaryEntry(BaseModel):
    text: str

# Modelo de diario
class Diary(Base):
    __tablename__ = "diary"
    id = Column(String, primary_key=True)
    user_email = Column(String, ForeignKey("users.email"))
    date = Column(Date, default=date.today)
    text = Column(String)
    emotion_estandar = Column(String)
    emotion_idioma = Column(String)

@app.post("/chat", response_model=AIResponse)
def chat_with_ai(user_query: UserQuery, authorization: Annotated[HTTPAuthorizationCredentials, Depends(security)], db: Session = Depends(get_db)):
    try:
        if not authorization:
            raise HTTPException(status_code=401, detail="Token no proporcionado")
        # Extraer email del token
        token = authorization.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_email = payload.get("sub")
        
        if not user_email:
            raise HTTPException(status_code=401, detail="Token inválido o expirado")
        
        # Generar un ID único para la interacción
        interaction_id = str(uuid.uuid4())
        
        # Crear mensaje en formato esperado
        messages = [{"role": "user", "content": user_query.question}]
        
        # Llamada a la API de Hugging Face Spaces
        result = client.predict(messages=messages, api_name="/predict")
        
        if result and isinstance(result, dict) and "response" in result:
            
            # Guardar la interacción en la base de datos
            new_history = UserHistory(
                user_email=user_email,
                interaction=user_query.question,
                id_interaction=interaction_id
            )
            db.add(new_history)
            db.commit()
            
            return AIResponse(response=result["response"])
        else:
            raise HTTPException(status_code=500, detail="Respuesta inesperada del agente IA")
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Función para generar un token JWT
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Ruta para el login
@app.post("/login")
async def login(credentials: UserCredentials, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == credentials.email).first()

    # Verificar si el usuario existe y si la contraseña es correcta (comparación en texto plano)
    if not user or credentials.password != user.password:
        raise HTTPException(status_code=401, detail="Correo electrónico o contraseña incorrectos")

    # Generar un nuevo token
    token = create_access_token(data={"sub": credentials.email}, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))

    # Sobrescribir el token en la base de datos
    user.token = token
    db.commit()

    return {"access_token": token, "token_type": "bearer"}

@app.post("/diary")
async def add_diary_entry(
    entry: DiaryEntry,
    authorization: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    db: Session = Depends(get_db)
):
    # Verificar si el token de autorización es válido
    if not authorization:
        raise HTTPException(status_code=401, detail="Token de autorización no proporcionado")
    
    token = authorization.credentials

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if not email:
            raise HTTPException(status_code=401, detail="Token inválido o expirado")
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")
    
    # Verificar token en base de datos
    user = db.query(User).filter(User.email == email).first()
    if not user or user.token != token:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")
    
    # Calcular la emoción del diario
    _, emotion_estandar, emotion_idioma = puntuar_texto(entry.text)

    # Crear entrada en el diario
    new_entry = Diary(
        id = str(uuid.uuid4()),
        user_email = email,
        text = entry.text,
        emotion_estandar = emotion_estandar, 
        emotion_idioma = emotion_idioma
    )
    db.add(new_entry)
    db.commit()

    return {"mensaje": "Entrada de diario añadida correctamente"}

@app.get("/history")
async def get_diary_history(authorization: Annotated[HTTPAuthorizationCredentials, Depends(security)], db: Session = Depends(get_db)):
    try:
        if not authorization:
            raise HTTPException(status_code=401, detail="Token no proporcionado")
        # Extraer email del token
        token = authorization.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_email = payload.get("sub")
        
        if not user_email:
            raise HTTPException(status_code=401, detail="Token inválido o expirado")

        diaries = db.query(Diary).filter(Diary.user_email == user_email).order_by(Diary.date.desc()).limit(5)

        history = []
        for diary in diaries:
            history.append(DiaryJson(
                id = diary.id,
                date=diary.date,
                text=diary.text,
                emotion_estandar=diary.emotion_estandar,
                emotion_idioma=diary.emotion_idioma
            ))

        return HistoryResponse(history=history)

    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/profile")
async def get_profile(authorization: Annotated[HTTPAuthorizationCredentials, Depends(security)], db: Session = Depends(get_db)):
    try:
        if not authorization:
            raise HTTPException(status_code=401, detail="Token no proporcionado")

        # Extraer email del token
        token = authorization.credentials.split("Bearer ")[-1]
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_email = payload.get("sub")
        
        if not user_email:
            raise HTTPException(status_code=401, detail="Token inválido o expirado")
        
        diaries = db.query(Diary).filter(Diary.user_email == user_email).all()
        texts = [diary.text for diary in diaries]
        scores = [puntuar_texto(text)[0] for text in texts]
        averages = calcular_media_puntuaciones(scores)
        levels = niveles_personalidad(averages)

        resultList = []
        for trait, score in levels.items():
            with open("emotions.json", "r", encoding="utf-8") as file:
                data = json.load(file)
                trait_features = list(filter(lambda x: x["emotion"] == trait and x["level"] == score, data["emotionsList"]))
                trait_json = TraitJson(trait=trait, score=score, description=trait_features[0]["description"])
                resultList.append(trait_json)

        return ScoreResponse(profile=resultList)
                
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))