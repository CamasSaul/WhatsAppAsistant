from dataclasses import dataclass


@dataclass
class Contact:
    name:str
    number:str

    def get_contact_info (self) -> str:
        return open(f'chats/{self.name}/{self.name}_info.txt').read()


    def get_boxes_info (self) -> list:
        """
        Retorna toda la información de las cajas de información (boxes) que tenga asignado el contacto."""
        boxes = open(f'chats/{self.name}/{self.name}_boxes.txt', encoding='utf-8').read().split('\n')
        return [open(f'boxes/{box.strip()}.txt', encoding='utf-8').read() for box in boxes if box]
    
    
    def get_context_info (self, tokens_length:int) -> list:
        """
        Retorna el historial de conversaciones según el número de carácters solicitados.

        #### Args:
        `tokens_length` : `int` Define cuantos caracteres de historial de conversación retornará.
        Este retornará los últimos tokens del historial.
        """
        history = open(f'chats/{self.name}/{self.name}.txt', encoding='utf-8').read()
        if len(history) >= tokens_length:
            return history[:-tokens_length]
        else:
            return history