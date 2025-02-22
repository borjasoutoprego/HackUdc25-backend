from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from jose import jwt, JWTError
from datetime import datetime, timedelta
import secrets

# Configuración de FastAPI
app = FastAPI()

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