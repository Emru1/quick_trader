import json


class QTraderMessage:
    '''
    Klasa reprezentująca wiadomość zgodną z ustalonym schematem.
    Umożliwia odbieranie danych, zapewniając przy tym walidację (na razie słabą xD)
    Przykładowe flow:
        KLIENT:
            message = QTraderMessage('auth', {'username': 'user', 'password': 'pass'})
            server.sendall(message.format_to_send)
        SERWER:
            message = QTraderMessage.receive_message(client)
    '''
    VALID_TYPES = ['auth', 'bet', 'list', 'logout', 'error']

    def __init__(self, message_type, message: dict):
        '''
        :param: message_type(str) - typ wiadomości. Zgodny z VALID_TYPES
        :param: message(dict) - wiadomość zapisana w słowniku (klucz:wartość)
        '''
        if message_type not in self.VALID_TYPES:
            raise Exception('Invalid message type')

        self.message_type = message_type

        if not type(message) is dict:
            raise Exception('Message must be a dictionary.')

        self.message = {}
        self.message['type'] = self.message_type
        self.message.update(message)

    def format_to_send(self):
        '''
        Koduje wiadomość w utf-8.
        WYWOŁYWAĆ PRZED WYSŁANIEM!

        return: zakodowana wiadomość stworzona ze słownika(bytes)
        '''
        json_message = json.dumps(self.message)
        json_size = len(json_message)
        return f'{str(json_size)}x{json_message}'.encode()

    @classmethod
    def receive_message(cls, guest_socket, separator='x'):
        '''
        MOŻNA WYWOŁYWAĆ BEZ STWORZENIA INSTANCJI KLASY!
        Odbiera i zwraca wiadomość od guest_socket

        :param: guest_socket(socket) - gniazdo, z którego chcemy odebrać wiadomość
        :param: separator(byte) - opcjonalne
        :eturn: message_data(dict) - odebrana wiadomość jako słownik

        '''
        recv_data = b''

        while separator.encode() not in recv_data:
            recv = guest_socket.recv(1)
            recv_data += recv

        try:
            message_size = int(recv_data[:-1].decode())
        except ValueError:
            raise Exception('Invalid incoming message')

        message_data = json.loads(guest_socket.recv(message_size))
        message_type = message_data.get('type', None)

        if not message_type or message_type not in cls.VALID_TYPES:
            raise Exception('Invalid incoming message')

        return message_data
