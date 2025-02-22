from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from gradio_client import Client
from fastapi import FastAPI, HTTPException, Depends, Header
from sqlalchemy import create_engine, Column, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from jose import jwt, JWTError
from datetime import datetime, timedelta
import secrets
import uuid
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Annotated

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
    email = Column(String, primary_key=True, index=True)
    password = Column(String)
    token = Column(String, nullable=True)

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

# Modelo de historial de usuario
class UserHistory(Base):
    __tablename__ = "user_history"
    user_email = Column(String, nullable=False)
    interaction = Column(String, nullable=False)
    id_interaction = Column(String, primary_key=True, nullable=False)

@app.post("/chat", response_model=AIResponse)
def chat_with_ai(user_query: UserQuery, authorization: Annotated[HTTPAuthorizationCredentials, Depends(security)], db: Session = Depends(get_db)):
    try:
        if not authorization:
            raise HTTPException(status_code=401, detail="Token no proporcionado")
        print(authorization.credentials)
        # Extraer email del token
        token = authorization.credentials.split("Bearer ")[-1]
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

# Ruta protegida que requiere autenticación
@app.get("/protegido")
async def ruta_protegida(token: str, db: Session = Depends(get_db)):
    try:
        # Verificar el token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Token inválido o expirado")
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")

    # Verificar si el token coincide con el almacenado en la base de datos
    user = db.query(User).filter(User.email == email).first()

    if not user or user.token != token:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")

    return {"mensaje": "Acceso concedido", "email": email}
