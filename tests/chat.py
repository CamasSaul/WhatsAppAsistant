from source.llm_model import generar_respuesta


if __name__ == '__main__':
    print('Chat para testear modelo.\n\n')

    while True:
        try:
            mensaje = input('Mensaje: ')
            respuesta = generar_respuesta(mensaje)
            print(f'Respuesta: {respuesta}')
        except KeyboardInterrupt:
            print('Finalizando.')
            break
        except Exception as e:
            print(f'Ocurrió un error: {e}')