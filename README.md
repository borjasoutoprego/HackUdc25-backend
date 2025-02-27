<img src="https://github.com/user-attachments/assets/760d46be-3162-4877-8af0-27793b8cc91b"/>

## Descripción

HackUdc25-backend es el backend del proyecto desarrollado en el hackathon **HackUDC 2025** como solución para el reto propuesto por la empresa patrocinadora **Kelea**. En esta aplicación realizada con FastAPI se desarrolla un asistente de Inteligencia Artificial que tiene dos roles: asistente para el apoyo emocional, y coach de bienestar y objetivos personales. Se desarrolla también un diario personal que identifica emociones en el texto. Además, la aplicación permite la clasificación de la personalidad según el modelo Big Five a través de las entradas de texto del usuario (tanto por el chat como por el diario). El proyecto dispone de dos contenedores Docker: uno para el front-end y otro para la base de datos. El proyecto está separado en dos repositorios, uno para front y otro para backend, por lo que la documentación relativa al front se encuentra en https://github.com/JanDuinkerken/HackUdc25-front

https://github.com/user-attachments/assets/32289498-e966-4d6d-b0f0-f5cb07d8e5f8

## Instalación

1. Clona el repositorio:
    ```sh
    git clone <URL_DEL_REPOSITORIO>
    cd HackUdc25-backend
    ```

2. Crea y activa un entorno virtual:
    ```sh
    python3 -m venv venv
    macOs/Linux: source venv/bin/activate  
    Windows: venv\Scripts\activate
    ```

3. Instala las dependencias:
    ```sh
    pip install -r requirements.txt
    ```

4. Levantar el contenedor de Docker que contiene la base de datos (desde la ruta \compose):
   ```
   docker compose up
   ```

6. Inicia la aplicación:
    ```sh
    uvicorn app:app --reload
    ```

## Funcionalidades

### Chatbot IA

- **Interacción con agente IA**: Los usuarios pueden conversar con un agente IA basado en el LLM [Qwen2.5-Coder-32B-Instruct](https://huggingface.co/Qwen/Qwen2.5-Coder-32B-Instruct). Este agente tiene dos roles:
  * Agente de `apoyo emocional`: Ofrece apoyo emocional, analiza sentimientos y emociones, y ayuda al usuario a manejar sus emociones.
  * Coach de `bienestar y objetivos`: Propone objetivos personalizados basados en el estado emocional del usuario y lo guía para mejorar su bienestar.
 Para cambiar de rol, el usuario deberá enviar al agente el mensaje: `"Cambiar a modo coach"/"Cambiar a modo apoyo emocional"`.

Mediante la API de gradio_client, la app realiza peticiones a este agente, el cual se encuentra alojado en el Hugging Face Spaces: [hackudc25](https://huggingface.co/spaces/borjasoutoprego/hackudc25), el cual se ha desarrollado también en el marco de este proyecto.

### Entradas de Diario

- **Añadir Entrada**: Los usuarios pueden añadir entradas de diario que son analizadas para determinar las emociones predominantes en ellas. Estas entradas pueden realizarse en cualquier idioma (castellano, gallego, inglés...) ya que la aplicación lo maneja de manera automática para realizar el análisis de sentimientos independientemente de este. Para realizar la clasificación de las emociones se utiliza el modelo [distilbert-base-uncased-go-emotions-student](https://huggingface.co/joeddav/distilbert-base-uncased-go-emotions-student), que clasifica los textos dándole probabilidades a 28 emociones.
- **Historial de Diario**: Existe un historial de las entradas de diario de cada usuario. Se pueden consultar las últimas 5 entradas, así como las emociones asociadas a ellas, con un código de colores que clasifica los días según emociones positivas, negativas o neutras.

### Gestión de Perfiles

- **Perfil de Usuario**: A partir de todas las entradas del usuario, la aplicación consigue categorizar la personalidad en el modelo Big Five (OCEAN). Esto se realiza a través del análisis de sentimientos y la relación de las emociones con los distintos tipos de personalidad del modelo. La categorización se realiza en 5 niveles, y mostramos un radar chart intuitivo y una pequeña descripción de cada nivel.

### Autenticación de Usuarios

- **Registro y Login**: Los usuarios pueden autenticarse mediante correo electrónico y contraseña, garantizando que las conversaciones con el chatbot, el perfilado de la personalidad y las entradas del diario son únicas y privadas para cada usuario, ya que solo pueden accederse a estas una vez autenticado.
- **Generación de Tokens JWT**: Se generan tokens JWT únicos para la autenticación de las solicitudes, que se eliminan una vez la sesión espira o se hace el logout.

## Detalles Técnicos

- **Framework**: FastAPI
- **Base de Datos**: PostgreSQL
- **Autenticación**: JWT
- **Cliente de IA**: Hugging Face Spaces
