import streamlit as st
from groq import Groq
import requests
from io import BytesIO

# Configuración de la página
st.set_page_config(page_title="Generador de Historias", page_icon="📖")

# Lista de géneros disponibles
GENEROS = ["Aventura", "Fantasía", "Ciencia Ficción", "Comedia", "Terror", "Romance"]

# Conexión con la API de Groq
def conectar_groq():
    api_key = st.secrets["CLAVE_API"]
    return Groq(api_key=api_key)

# Función para generar historia
def generar_historia(cliente, prompt, genero, longitud):
    mensaje = f"Escribe una historia del género {genero}, empezando con: {prompt}. Debe tener {longitud} palabras."
    respuesta = cliente.chat.completions.create(
        model="mixtral-8x7b-32768",  # Puedes cambiar el modelo según prefieras
        messages=[{"role": "user", "content": mensaje}],
        #max_tokens=longitud,  # Ajusta la longitud de la respuesta
        temperature=0.7  # Para generar texto más creativo
    )
    return respuesta.choices[0].message.content

def textToSpeechElevenLabs(text,APIKey):
    """Función que usa la API de Eleven Labs para tomar un texto y retornar un audio en bytes
       usando el método de Text to Speech
       https://elevenlabs.io/docs/api-reference/text-to-speech
    Args:
        text (str): Texto que se desea convertir a audio
        APIKey (str): API Key de la cuenta de Eleven Labs

    Returns:
        bytes: Audio en formato mpeg
    """    

    #Define el tamaño de los fragmentos de datos que se recibirán desde el servidor.
    CHUNK_SIZE = 1024 
    # Es la dirección del endpoint de la API de Eleven Labs para convertir texto a voz
    url = "https://api.elevenlabs.io/v1/text-to-speech/ZQe5CZNOzWyzPSCn5a3c" 
    
    # El código pNInz6obpgDQGcFmaJgB corresponde a la voz a utilizar

    # Encabezado del request
    headers = {
    "Accept": "audio/mpeg",
    "Content-Type": "application/json",
    "xi-api-key": APIKey
    }

    # Datos del request
    data = {
    "text": text,
    "model_id": "eleven_multilingual_v2",
    "voice_settings": {
        "stability": 0.5,
        "similarity_boost": 0.5
    }
    }

    response = requests.post(url, json=data, headers=headers)
    
    #  Un contenedor en memoria que se usa para almacenar los datos de audio.
    audio_stream = BytesIO()
    
    # Escribe cada parte de los datos de audio en la transmisión
    # response.iter_content: Descarga el audio en partes o "fragmentos" (chunks) de tamaño CHUNK_SIZE.
    # Cada fragmento se agrega al audio_stream.
    for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
        if chunk:
            audio_stream.write(chunk)
    
    # Restablecer la posición de la transmisión al principio
    audio_stream.seek(0)
    
    # Devuelve la transmisión para un uso posterior
    return audio_stream

# Interfaz de Streamlit
def main():
    st.title("📖 Generador de Historias con IA")
    st.write("Escribe una frase inicial y deja que la inteligencia artificial cree una historia para ti.")

    # Entrada del usuario
    prompt = st.text_input("Escribe la frase inicial de tu historia:", "")
    genero = st.selectbox("Selecciona el género de tu historia:", GENEROS)
    longitud = st.slider("¿Cuántas palabras debería tener la historia?", min_value=50, max_value=500, step=50, value=200)

    # Conexión a Groq
    cliente = conectar_groq()

    # Botón para generar historia
    if st.button("Generar Historia"):
        if prompt.strip(): #Verifica que el usuario haya mandado un mensaje
            with st.spinner("Generando tu historia y preparando el audio..."):
                # Generar historia
                historia = generar_historia(cliente, prompt, genero, longitud)
                # Generar audio
                audio = textToSpeechElevenLabs(historia, st.secrets["CLAVE_ELEVENLAB"])
            
            # Mostrar resultados una vez que ambos procesos terminen
            st.subheader("Tu Historia:")
            st.write(historia)
            if audio: # verifica si el objeto audio tiene contenido válido
                st.audio(audio, format="audio/mpeg", autoplay=True)  # Reproduce el audio directamente
    else:
        st.warning("Por favor, escribe una frase inicial.")


# Ejecutar la aplicación
if __name__ == "__main__":
    main()
