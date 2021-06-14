import socket
import json
import time
import ssl
from qtrader_message import QTraderMessage

class Client:

    def __init__(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            context = ssl.create_default_context(
                ssl.Purpose.CLIENT_AUTH, cafile='tls.cert')
            # context.load_cert_chain(certfile='tls.cert', keyfile='tls.key')
            s = socket.create_connection(("localhost", 5555))
            ssl_socket = ssl.wrap_socket(s)
        except socket.error:
            print("Socket error")

        self.ssl_socket.close()

    def check_token(self):
        if self.message["token"] != self.token:
            print("Błąd uwierzytelnienia! Połączenie nie jest bezpieczne, skontaktuj się z administracją")
            return False
        else: return True

    def dload_list(self):
        QTraderMessage("list", {"token":self.token})
        self.ssl_socket.sendall(QTraderMessage.format_to_send())
        self.message = QTraderMessage.receive_message(self.ssl_socket)
        self.check_token()
        if self.message["error"]:
            print("Something's wrong with downloading list! Trying again")
            time.sleep(5)
            self.dload_list()
        else:
            print(self.message["list"])

    def log_in(self, username, password):
        self.username = username
        QTraderMessage("auth", {"username":username, "password":password})
        self.ssl_socket.sendall(QTraderMessage.format_to_send())
        self.message = QTraderMessage.receive_message(self.ssl_socket)
        if self.message["error"]:
            print("Connection lost! Try again")
            print(self.message["error"])
            self.log_in()
        elif self.message["type"] == "login":
            self.token = self.message["token"]

    def log_out(self):
        QTraderMessage("logout", {"username":self.username, "token":self.token})
        self.ssl_socket.sendall(QTraderMessage.format_to_send())
        self.message = QTraderMessage.receive_message(self.ssl_socket)
        return self.check_token()

    def bet(self, new_price):
        QTraderMessage("bet", {"price":new_price, "token":self.token})
        self.ssl_socket.sendall(QTraderMessage.format_to_send())


    def trading(self):
        #musisz tutaj dodać wątek nasłuchiwania który aktualizuje zmienną "price" i odbiera informacje od serwera
        #użyj funkcji bet do wysłania nowej ceny

        pass
        #CDN


