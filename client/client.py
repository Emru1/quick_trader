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
        self.actual_price = None
        self.ssl_socket = None

    def check_token(self):
        if self.message["token"] != self.token:
            print(
                "Błąd uwierzytelnienia! Połączenie nie jest bezpieczne, skontaktuj się z administracją")
            return False
        else:
            return True

    def dload_list(self):
        QTraderMessage("list", {"token": self.token})
        self.ssl_socket.sendall(QTraderMessage.format_to_send())
        self.message = QTraderMessage.receive_message(self.ssl_socket)
        self.check_token()
        if self.message["error"]:
            print("Something's wrong with downloading list! Trying again")
            time.sleep(5)
            self.dload_list()
        else:
            print(self.message["list"])

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
            received_message = QTraderMessage.receive_message(self.ssl_socket)

            print('Logout succesfully!')

            self.ssl_socket.close()
            self.token = None
            self.username = None
            self.password = None

        else:
            print('You are not logged in!')
            return

    def bet(self, how_much_to_add):
        bet_temp = self.actual_price + how_much_to_add
        QTraderMessage("bet", {"price": bet_temp, "token": self.token})
        self.ssl_socket.sendall(QTraderMessage.format_to_send())

    def listen(self):
        '''
        Nasłuchiwanie komunikatów od serwera
        '''
        if self.token:
            while True:
                print('HALO HALO')
                try:
                    received_message = QTraderMessage.receive_message(
                        self.ssl_socket)
                    print(received_message)
                except ConnectionError:
                    print('Connection problem')


if __name__ == "__main__":
    test_client = Client()
    test_client.login('test', '123')
    test_client.logout()
