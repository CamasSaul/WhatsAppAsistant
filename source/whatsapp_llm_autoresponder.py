import csv
from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel, Field

from source.datamodel import Contact
from source.llm_model import generar_respuesta, obtener_modelo_info, iniciar_modelo_en_background

app = FastAPI(title="AutoResponder WhatsApp con LLM Local")

class Message(BaseModel):
    from_: str = Field(..., description="Remitente del mensaje")
    body: str
    
    class Config:
        allow_population_by_field_name = True
        fields = {'from_': {'alias': 'from'}}


# Iniciar carga del modelo en segundo plano
modelo_thread = iniciar_modelo_en_background()

# Crear lista de contactos
contactos = []
with open('contactos_whatsapp.csv', mode='r', encoding='utf-8') as file:
    contactos_admitidos = open('contactos_admitidos.txt', encoding='utf-8').read().split()
    reader = csv.DictReader(file)
    for contacto in reader:
        nombre = contacto['Nombre']
        numero = contacto['Número']
        if nombre in contactos_admitidos:
            contactos.append(Contact(nombre, numero))



@app.get("/")
async def root():
    modelo_info = obtener_modelo_info()
    return {
        "status": "API funcionando",
        "modelo": modelo_info
    }



@app.post("/analyze")
async def analyze(msg: Message):
    try:
        print(f'Mensaje recibido [{msg.from_}: {msg.body}]')
        number = msg.from_[:-5]
        # Extraer el contacto y generar respuesta
        for c in contactos:
            if c.number == number:
                respuesta = generar_respuesta(msg.body, c)
                break
        
        print(f"Respuesta del modelo: {respuesta}")

        no_responder_frases = ["no responder", "no es necesario responder", "ignorar mensaje"]
        if any(frase in respuesta.lower() for frase in no_responder_frases):
            return {"reply": None, "should_reply": False, "reason": "Mensaje no requiere respuesta"}
        else:
            return {"reply": respuesta, "should_reply": True}
    except Exception as e:
        print(f"Error al generar respuesta: {e}")
        return {"error": str(e), "reply": None, "should_reply": False}



@app.get("/test")
async def test_model():
    try:
        test_input = "¿Cómo estás hoy?"
        respuesta = generar_respuesta(test_input)
        return {"test_prompt": test_input, "response": respuesta}
    except Exception as e:
        return {"error": str(e)}



@app.get("/reset-model")
async def reset_model():
    """Endpoint para reiniciar el modelo si hay problemas"""
    from source.llm_model import inicializar_modelo, _model_lock
    import importlib
    import source.llm_model as llm_model
    
    try:
        with _model_lock:
            # Reiniciar las variables globales
            llm_model._model = None
            llm_model._tokenizer = None
            
        # Recargar el módulo para asegurarse de que todo está fresco
        importlib.reload(llm_model)
        
        # Inicializar de nuevo el modelo
        llm_model.inicializar_modelo("test_dummy" if app.debug else None)
        
        return {"status": "success", "message": "Modelo reiniciado correctamente"}
    except Exception as e:
        return {"status": "error", "message": f"Error al reiniciar modelo: {str(e)}"}
        


@app.get("/debug")
async def debug_info():
    """Devuelve información de depuración del sistema"""
    import sys
    import torch
    import os
    
    # Obtener información sobre las conversaciones
    from source.llm_model import conversaciones
    
    return {
        "python_version": sys.version,
        "torch_version": torch.__version__,
        "cuda_available": torch.cuda.is_available(),
        "cuda_version": torch.version.cuda if torch.cuda.is_available() else None,
        "cwd": os.getcwd(),
        "conversations_count": len(conversaciones),
        "last_conversation_length": len(conversaciones[-1]) if conversaciones else 0,
        "memory_usage": {
            "torch_reserved": f"{torch.cuda.memory_reserved() / 1024**3:.2f} GB" if torch.cuda.is_available() else None,
            "torch_allocated": f"{torch.cuda.memory_allocated() / 1024**3:.2f} GB" if torch.cuda.is_available() else None
        }
    }



if __name__ == "__main__":
    import uvicorn
    # Iniciar carga del modelo en segundo plano
    print("Iniciando servidor FastAPI con generador de respuestas basado en LLM...")
    print("El modelo se cargará en segundo plano. Puede tardar unos minutos...")
    
    # Establecer modo debug para usar el modelo dummy durante desarrollo
    app.debug = True
    
    uvicorn.run(app, host="0.0.0.0", port=8000)