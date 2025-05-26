import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from transformers import AutoTokenizer
import platform
import psutil
import threading

from source.datamodel import Contact

# Variable global para almacenar el modelo y tokenizador
_model = None
_tokenizer = None
_model_lock = threading.Lock()  # Para garantizar acceso seguro en entorno multithread


def mostrar_info_sistema():
    """Muestra información del sistema y GPU disponible."""
    print("Información del sistema:")
    print(f"Sistema operativo: {platform.system()} {platform.version()}")
    print(f"Procesador: {platform.processor()}")
    print(f"RAM disponible: {psutil.virtual_memory().available / (1024 ** 3):.2f} GB")
    
    # Verificar disponibilidad de CUDA
    print("\nInformación de GPU:")
    if torch.cuda.is_available():
        print(f"CUDA disponible: Sí")
        print(f"Dispositivo CUDA: {torch.cuda.get_device_name(0)}")
        print(f"Versión CUDA: {torch.version.cuda}")
        print(f"Memoria total GPU: {torch.cuda.get_device_properties(0).total_memory / (1024**3):.2f} GB")
        print(f"Memoria disponible GPU: {torch.cuda.memory_reserved(0) / (1024**3):.2f} GB")
    else:
        print("CUDA no disponible. El modelo se ejecutará en CPU.")

def cargar_modelo(nombre_modelo="NousResearch/Nous-Hermes-2-Mistral-7B-DPO", cuantizacion=True):
    """
    Carga un modelo de lenguaje pequeño optimizado para GPU con memoria limitada.
    
    Args:
        nombre_modelo: Nombre del modelo de Hugging Face a cargar
        cuantizacion: Si se debe usar cuantización para reducir el uso de memoria
    
    Returns:
        modelo, tokenizador
    """
    print(f"\nCargando modelo: {nombre_modelo}")
    
    # Configurar cuantización si está habilitada
    quantization_config = None
    if cuantizacion and torch.cuda.is_available():
        quantization_config = BitsAndBytesConfig(
            bnb_4bit_compute_dtype=torch.float16,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_use_double_quant=True
        )
        print("Cuantización de 4-bits activada")
    
    # Configurar dispositivo
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Usando dispositivo: {device}")
    
    # Cargar tokenizador
    tokenizer = AutoTokenizer.from_pretrained(nombre_modelo)
    
    # Cargar modelo con configuración optimizada
    modelo = AutoModelForCausalLM.from_pretrained(
        nombre_modelo,
        quantization_config=quantization_config,
        device_map="auto",
        torch_dtype=torch.float16 if device == "cuda" else torch.float32,
        low_cpu_mem_usage=True
    )
    
    return modelo, tokenizer

def generar_texto(modelo, tokenizer, prompt, max_length=100):
    """
    Genera texto basado en un prompt dado.
    
    Args:
        modelo: Modelo cargado
        tokenizer: Tokenizador correspondiente
        prompt: Texto de entrada para el modelo
        max_length: Longitud máxima de tokens a generar
    
    Returns:
        Texto generado
    """
    # Tokenizar entrada
    inputs = tokenizer(prompt, return_tensors="pt")
    
    # Mover a GPU si está disponible
    if torch.cuda.is_available():
        inputs = {k: v.to("cuda") for k, v in inputs.items()}
    
    # Generar texto con parámetros ajustados
    with torch.no_grad():
        outputs = modelo.generate(
            **inputs,
            max_new_tokens=max_length,
            do_sample=True,
            temperature=0.5,  # Aumentado ligeramente para más creatividad
            top_p=0.70,       # Aumentado para considerar más opciones
            top_k=50,         # Limitar a las 50 mejores opciones
            repetition_penalty=1.2,  # Penalizar repeticiones
            pad_token_id=tokenizer.eos_token_id if tokenizer.eos_token_id is not None else tokenizer.pad_token_id
        )
    
    # Decodificar y devolver el texto generado
    texto_generado = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return texto_generado

def extraer_ultima_respuesta(prompt, salida: str) -> str:
    """
    Resta el prompt de la salida del modelo y devuelve la primera línea de la nueva respuesta.
    """
    # Asegurarse de que la salida contiene el prompt
    if not salida.startswith(prompt):
        return "[La salida no contiene el prompt al inicio]"
    
    # Eliminar el prompt
    if salida.startswith(prompt):
        resto = salida[len(prompt):]
        return resto.split('\n')[0]
    else:
        return 'Error'
        

def get_prompt(mensaje_usuario:str, contacto:Contact):
    # Construir el prompt
    prompt = open('prompt.txt', encoding='utf-8').read()
    prompt += 'A continuación, las cajas de información:\n\n'
    for b in contacto.get_boxes_info():
        prompt += b
    prompt += '\n\nINFORMACIÓN DEL CONTACTO:\n' + contacto.get_contact_info()
    prompt += '\nHistorial de conversaciones:\n' + contacto.get_context_info(50)
    prompt += f'\n\nPor último, el mensaje del usuario: {mensaje_usuario}'
    prompt += f'\n\nDelvuelve únicamente la respuesta, Respuesta: '
    return prompt


def inicializar_modelo(modelo_seleccionado="NousResearch/Nous-Hermes-2-Mistral-7B-DPO"):
    """
    Inicializa el modelo y lo almacena en variables globales para su reutilización.
    """
    global _model, _tokenizer
    
    with _model_lock:
        if _model is None:
            mostrar_info_sistema()
            
            # Para facilitar las pruebas, permitir un valor dummy si no se puede cargar el modelo real
            if modelo_seleccionado == "test_dummy":
                class DummyModel:
                    def generate(self, **kwargs):
                        # Simular una respuesta del modelo
                        return [_tokenizer.encode("Hola, soy un modelo de prueba. ¿En qué puedo ayudarte hoy?")]
                
                class DummyTokenizer:
                    def __init__(self):
                        self.eos_token_id = 0
                        self.pad_token_id = 0
                    
                    def __call__(self, text, **kwargs):
                        return {"input_ids": torch.tensor([[0, 1, 2, 3]]), "attention_mask": torch.tensor([[1, 1, 1, 1]])}
                    
                    def decode(self, token_ids, **kwargs):
                        if isinstance(token_ids, list):
                            return "Hola, soy un modelo de prueba. ¿En qué puedo ayudarte hoy?"
                        return "Texto decodificado de prueba"
                    
                    def encode(self, text):
                        return [0, 1, 2, 3, 4, 5]
                
                _model = DummyModel()
                _tokenizer = DummyTokenizer()
                print("Usando modelo dummy para pruebas")
            else:
                try:
                    _model, _tokenizer = cargar_modelo(modelo_seleccionado, cuantizacion=True)
                    print("Modelo cargado y listo para recibir solicitudes.")
                except Exception as e:
                    print(f"Error al cargar el modelo: {e}")
                    print("Intentando modelo alternativo...")
                    try:
                        _model, _tokenizer = cargar_modelo("TinyLlama/TinyLlama-1.1B-Chat-v1.0", cuantizacion=True)
                        print("Modelo alternativo cargado.")
                    except Exception as e2:
                        print(f"Error al cargar modelo alternativo: {e2}")
                        raise

def generar_respuesta(mensaje_usuario:str, contacto:Contact):
    """
    Función principal para generar una respuesta utilizando el modelo.
    Esta función será llamada por el servidor FastAPI.
    """
    global _model, _tokenizer
    
    # Asegurarse de que el modelo esté cargado
    if _model is None:
        inicializar_modelo()
    
    with _model_lock:  # Para garantizar acceso seguro en entorno multithread
        # Generar el prompt con el mensaje del usuario
        prompt = get_prompt(mensaje_usuario, contacto)
        print(f'PROMPT[\n{prompt}\n]')
        
        # Generar la respuesta
        respuesta_completa = generar_texto(_model, _tokenizer, prompt, max_length=150)
        print(f'RESPUESTA COMPLETA[{respuesta_completa}]')
        
        # Extraer solo la parte relevante de la respuesta
        respuesta_limpia = extraer_ultima_respuesta(prompt, respuesta_completa)        
        return respuesta_limpia


def obtener_modelo_info():
    """
    Devuelve información sobre el modelo cargado.
    """
    global _model, _tokenizer
    
    if _model is None:
        return {"status": "No cargado", "modelo": "Ninguno"}
    
    # Intentar obtener el nombre del modelo
    try:
        nombre_modelo = _model.config._name_or_path
    except:
        nombre_modelo = "Desconocido"
    
    return {
        "status": "Cargado",
        "modelo": nombre_modelo,
        "dispositivo": "CUDA" if torch.cuda.is_available() else "CPU"
    }

# Inicializar el modelo en un hilo separado para no bloquear el inicio del servidor
def iniciar_modelo_en_background():
    thread = threading.Thread(target=inicializar_modelo)
    thread.daemon = True
    thread.start()
    return thread