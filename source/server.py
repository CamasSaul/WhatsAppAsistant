import httpx
import time
from datetime import datetime
from fastapi import FastAPI, Response
from google import genai

from datamodel import Message, AskRequest
from db_manager import DBManager

prompt = f'''
    Eres un asistente de mensajería de whatsapp.
    Tu objetivo es responder a los mensjajes porque el usario está ocupado.
    Solo, al inicio de la conversación, tienes que informar que eres un asistente y en que está ocupado el usuario.
    Trata de ser lo más natural posible.
    Tienes una serie de acciones que puedes realizar, cada acción la invocas con un comando.
    Solo genera la respuesta, los comandos van siempre al final de la respuesta.
    El usuario no debe saber acerca de los comandos.
    Los comandos son:
        Comando | Descripción | Uso
        /record | Guarda información en el registro de conversación para mas tarde ser analizado por el usuario. | <texto breve>
        /reminder | Guarda un recordatorio para el usuario. | <timestamp ISO-8601> <frase descriptiva>
        /notify: Notifica inmediatamente al usuario. Esto es solo en emergencias. | <asunto>
        /sendfile: Envía un archivo al conteacto en caso de que lo solicite y esté disponible. | <nombre completo del archivo>

    Ejemplos:
        /record LLevar al perro al veterinario.
        /reminder 2023-08-24T10:00:00 Recoger el paquete de la oficina.
        /notify Mamá pide ayuda.
        /sendfile Factura del mes.

    INFO GENERAL:
    Usuario: Saul
    Ocupado en: Junta de trabajo.
    Número de teléfono: 5217341810854
    Son las: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

    HISTORIAL DEL LA CONVERSACIÓN ACTUAL: (Contesta sin incluir "Asistente:")
'''

db = DBManager()

def construir_historial (id):
    historial = ''
    for row in db.fetch_messages(f'sender = "{id}"'):
        timestamp, from_, content, type = row
        response = db.fetch_responses(f'contact_id = "{id}" AND respond_to = {timestamp}')
        formated_timestamp = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
        if response:
            historial += f'[{formated_timestamp}] \t{from_}: {content}\n\t\tAsistant: {response[0][2]}\n'
        else:
            historial += f'[{formated_timestamp}] \t{from_}: {content}\n'
    return historial

# Initialize FastAPI app
app = FastAPI()

# Initialize Google AI client
client = genai.Client(api_key='')


# Root endpoint
@app.get('/')
async def root ():
    return {'status': 'OK'}


# Called on new message
@app.post('/message')
async def post_message(message: Message):
    print(f'Mensaje recibido: [{message.content}] de [{message.from_}]')
    db.save_message(message.timestamp, message.from_, message.content, message.type)

    # Si el conacto esta en la lista blanca, generar respuesta
    if message.from_ in ['5217776311275@c.us', '5217775104055@c.us', '5217772996227@c.us']:
        print(prompt + construir_historial(message.from_))
        # Generar respuesta usando el modelo de IA
        generated_response = client.models.generate_content(
                model='gemini-2.0-flash',
                contents=prompt + construir_historial(message.from_)
            ).text

        generated_response = generated_response.split('/record')[0]
        generated_response = generated_response.split('/notify')[0]
        generated_response = generated_response.split('/reminder')[0]
        generated_response = generated_response.split('/sendfile')[0]
        
        # Enviar respuesta al endpoint de whatsapp
        event = {
            'id': message.from_,
            'content': generated_response
        }

        async with httpx.AsyncClient() as _client:
            try:
                response = await _client.post(
                    "http://localhost:3700/send",
                    json=event
                )
                if response.status_code == 200:
                    db.save_response(int(time.time() * 1000), message.from_, generated_response, message.timestamp)
                    return {'status': 'OK'}
                else:
                    print(f'Error code: {response.status_code}')
                    return {'status': 'Response not OK', 'reason': f'Error code: {response.status_code}'}
                
            except httpx.HTTPError as e:
                print("Error al enviar al endpoint:", e)
                return {"error": str(e)}

    return Response(content='Message ignored.', status_code=204)


# Called to ask a question
@app.post('/ask')
async def ask (request: AskRequest):
    response = client.models.generate_content(model='gemini-2.0-flash',contents=request.message)
    return response


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=3701, log_level='debug')