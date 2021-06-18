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

        self.actual_price = None
        self.current_leader = None
        self.count = None
        self.auction_started = None

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
            s = socket.create_connection(("localhost", 5556))
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

        else:
            print('You are not logged in!')
            return

    def bet(self, how_much_to_add):
        print(f'NOWA:{how_much_to_add}')
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
                        self.message_handler(received_message)
                        yield received_message
                except ConnectionError:
                    print('Connection problem')

    def message_handler(self, message):
        if message['type'] == 'info' and message['started'] is True:
            self.count = message['end_time'] * 10
            self.actual_price = message['current_price']
            self.current_leader = message['leader']
            self.auction_started = True

        if message['type'] == 'bet':
            self.count = message['end_time'] * 10
            self.actual_price = message['current_price']
            self.current_leader = message['leader']


if __name__ == "__main__":
    test_client = Client()
    test_client.login('test', '123')
    test_client.logout()
