# HackUdc25-backend

## Descripción


HackUdc25-backend es el backend del proyecto desarrollado en el hackathon HackUDC como solución para el reto propuesto por la empresa patrocinadora Kelea. Es una aplicación desarrollada con FastAPI que proporciona funcionalidades para la creación de un asistente de Inteligencia Artificial para apoyo emocional, a través de un chatbot especialmente diseñado para el manejo de las emociones y un diario personal que obtiene emociones del texto. Además, la aplicación permite la clasificación de la personalidad según el modelo Big Five a través de las entradas de texto del usuario (tanto por el chat como por el diario). Todo el proyecto está contenido en un docker, donde se encuentran front-end, back-end y bases de datos.

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

4. Configura la base de datos:
    - Asegúrate de tener PostgreSQL instalado y ejecutándose.
    - Modifica la URL de la base de datos en [app.py](http://_vscodecontentref_/2) si es necesario:
        ```python
        DATABASE_URL = "postgresql://postgres:hackudc@127.0.0.1:5432/hackudc"
        ```

5. Inicia la aplicación:
    ```sh
    uvicorn app:app --reload
    ```

## Funcionalidades

### Consultas a IA

- **Chat con IA**: Los usuarios pueden conversar con un modelo LLM, al que se le ha realizado un proceso de prompt-engeneering para que sea especialmente empático.

### Entradas de Diario

- **Añadir Entrada**: Los usuarios pueden añadir entradas de diario que son analizadas para determinar emociones. Estas entradas pueden realizarse en cualquier idioma (castellano, gallego, inglés...) ya que la aplicación lo maneja de manera automática para realizar el análisis de sentimientos independientemente de este.
- **Historial de Diario**: Existe un historial de las entradas de diario de cada usuario. Se pueden consultar las emociones asociadas a las últimas entradas de manera tanto visual (a través de colores) como explícita.

### Gestión de Perfiles

- **Perfil de Usuario**: A partir de todas las entradas del usuario, la aplicación consigue categorizar la personalidad en el modelo Big Five (OCEAN). Esto se realiza a través del análisis de sentimientos y la relación de las emociones con los distintos tipos de personalidad del modelo. La categorización se realiza en 5 niveles, y mostramos un gráfico intuitivo y una pequeña descripción de cada nivel.

### Autenticación de Usuarios

- **Registro y Login**: Los usuarios pueden autenticarse mediante correo electrónico y contraseña, garantizando que las conversaciones con el chatbot, el perfilado de la personalidad y las entradas del diario son únicas y privadas para cada usuario.
- **Generación de Tokens JWT**: Se generan tokens JWT para la autenticación de las solicitudes.

## Detalles Técnicos

- **Framework**: FastAPI
- **Base de Datos**: PostgreSQL
- **Autenticación**: JWT
- **Cliente de IA**: Hugging Face Spaces
- **Librerías Principales**:
    - [fastapi](http://_vscodecontentref_/3)
    - [sqlalchemy](http://_vscodecontentref_/4)
    - [gradio_client](http://_vscodecontentref_/7)


## Licencia

Este proyecto está licenciado bajo los términos de la licencia especificada en el archivo LICENSE.