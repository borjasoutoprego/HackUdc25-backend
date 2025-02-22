from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from gradio_client import Client

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Client de Hugging Face Spaces
client = Client("borjasoutoprego/hackudc25")

# Modelo de datos de entrada
class UserQuery(BaseModel):
    question: str

# Modelo de datos de salida
class AIResponse(BaseModel):
    response: str

@app.post("/chat", response_model=AIResponse)
def chat_with_ai(user_query: UserQuery):
    try:
        # mensaje en el formato esperado por la API
        messages = [{"role": "user", "content": user_query.question}]
        
        # Llamada a la API de Hugging Face Spaces
        result = client.predict(messages=messages, api_name="/predict")
        
        # Extrae la respuesta del agente IA
        if result and isinstance(result, dict) and "response" in result:
            return AIResponse(response=result["response"])
        else:
            raise HTTPException(status_code=500, detail="Respuesta inesperada del agente IA")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))