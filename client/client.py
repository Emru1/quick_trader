import socket
import json
import time
import ssl
from qtrader_message import QTraderMessage


class Client:
    '''
    Klasa reprezentująca użytkownika (klienta) licytacji.
    Instancja używana w GUI
    '''

    def __init__(self):
        self.username = None
        self.password = None
        self.token = None
        self.ssl_socket = None

        self.item_name = None
        self.actual_price = None
        self.current_leader = None
        self.count = None
        self.auction_started = None
        self.date_auction_start_time = None

    def login(self, username, password):
        '''
        Logowanie użytkownika.
        :param: username(str) - nazwa użytkownika
        :param: password(str) - hasło użytkownika
        :return: (bool, str) - tupla zwracająca czy udało się zalogować z ewentualnym numerem błędum
        '''
        print(username, password)
        try:
            # context = ssl.create_default_context(
            # ssl.Purpose.CLIENT_AUTH, cafile='tls.cert')
            # context.load_cert_chain(certfile='tls.cert', keyfile='tls.key')
            s = socket.create_connection(("localhost", 5555))
            self.ssl_socket = ssl.wrap_socket(s)
            print(self.ssl_socket.version())
        except socket.error as e:
            print(e)

        if not self.token:
            self.username = username
            self.password = password
            login_message = QTraderMessage(
                "auth", {"username": username, "password": password})

            self.ssl_socket.sendall(login_message.format_to_send())
            received_message = QTraderMessage.receive_message(self.ssl_socket)

            if received_message['type'] == 'error':
                print('Connection lost! Try again')
                print(received_message['error'])
                return False, received_message['error']

            elif received_message['type'] == 'auth':
                print('Logged in!')
                self.token = received_message['token']
                print(self.token)
                return True, None
        else:
            print('You are already logged in!')
            return False, None

    def logout(self):
        if self.token:
            logout_message = QTraderMessage(
                "logout", {"username": self.username, "token": self.token})
            self.ssl_socket.sendall(logout_message.format_to_send())
            # received_message = QTraderMessage.receive_message(self.ssl_socket)

            print('Logout succesfully!')

            self.ssl_socket.close()
            self.token = None
            self.username = None
            self.password = None

            self.actual_price = None
            self.auction_started = None
            self.current_leader = None
            self.count = None

        else:
            print('You are not logged in!')
            return

    def bet(self, how_much_to_add):
        if self.token and self.actual_price:
            bet_temp = self.actual_price + how_much_to_add
            self.ssl_socket.sendall(QTraderMessage(
                "bet", {"price": bet_temp, "token": self.token, 'username': self.username}).format_to_send())

    def listen(self):
        '''
        Nasłuchiwanie komunikatów od serwera
        '''
        if self.token:
            while True:
                try:
                    received_message = QTraderMessage.receive_message(
                        self.ssl_socket)
                    if received_message:
                        gui_status = self.message_handler(received_message)
                        if gui_status in ['auction_started', 'auction_updated', 'error_message', 'auction_not_started_yet', 'auction_ended']:
                            yield gui_status
                except ConnectionError:
                    print('Connection problem')

    def message_handler(self, message):
        '''
        Sprawdza, co potrzeba i zwraca komunikat do GUI, żeby np. zaktualizować dane

        '''
        message_type = message['type']
        if message_type == 'info':
            if message['started'] is True:
                if message['end_time'] == 0:
                    # KONIEC LICYTACJI -> WYSWIETL OKIENKO
                    self.actual_price = message['current_price']
                    self.current_leader = message['leader']
                    self.auction_started = False
                    self.date_auction_start_time = None
                    return 'auction_ended'
                
                # LICYTACJA ROZPOCZĘtA USTAW POCZĄTKOWE WARTOŚCI
                self.item_name = message['name']
                self.count = message['end_time'] * 10
                self.actual_price = message['current_price']
                self.current_leader = message['leader']
                self.auction_started = True
                return 'auction_started'

            if message['started'] is False:
                # LICYTACJA JESZCZE NIE ROZPOCZĘTA ->  WYŚWIETL OKNO Z KOMUNIKATEM
                self.item_name = message['name']
                self.actual_price = message['current_price']
                self.auction_started = True
                self.date_auction_start_time = message['start_time']
                return 'auction_not_started_yet'

        elif message_type == 'bet':
            # LICYTACJA PRZEBITA - ZAKTUALIZUJ
            self.count = message['end_time'] * 10
            self.actual_price = message['current_price']
            self.current_leader = message['leader']
            return 'auction_updated'

        elif message_type == 'error' and message['error'] == 7:
            # NI MA LICYTACJI NA SERWERZE -> WYŚWIETl OKNO Z KOMUNIKATEM
            return 'error_message'


    def get_info(self):
        if self.token:
            self.ssl_socket.sendall(QTraderMessage(
                'info', {'username': self.username, 'token': self.token}).format_to_send())


if __name__ == "__main__":
    test_client = Client()
    test_client.login('test', '123')
    test_client.logout()
