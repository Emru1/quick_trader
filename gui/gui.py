
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QMainWindow, QApplication, QStackedWidget, QMessageBox
from PyQt5 import uic
import time
from threading import Thread
import socket
import sys
sys.path.append('\quick_trader\client')
from qtrader_message import QTraderMessage
from client import Client


class ClientWorkerThread(QThread):
    udpate = pyqtSignal(tuple)

    def __init__(self, client, parent=None):
        super().__init__(parent=parent)
        self.client = client

    def run(self):
        print('HALO HALO')
        messages = self.client.listen()

        for message in messages:
            print(f'WATEK: {message}')
            if message['type'] == 'info':
                status = (message['name'], message['start_price'])
                self.udpate.emit(status)

    def stop(self):
        self.terminate()


class LoginWindow(QMainWindow):
    '''
    Okno logowania
    '''

    def __init__(self):
        super().__init__()
        uic.loadUi('login.ui', self)
        self.show()


class MainWindow(QMainWindow):
    '''
    Główne okno programu - okno licytacji
    '''

    def __init__(self):
        super().__init__()
        uic.loadUi('logged.ui', self)
        self.show()


class GUI():
    '''
    Klasa GUI - interfejs użytkownika.
    Zawiera:
        main_scene - główna scena intefejsu (QStackedWidget), łatwe przełączanie się pomiędzy oknami.
        login_window - okno LoginWindow()
        main_window - okno MainWindow()
        username - nazwa użytkownika, domyślnie None. CHWILOWO. TUTAJ BĘDZIE KLIENT
        logged - zalogowany(bool). CHWILOWO JAK WYŻEJ
        worker - wątek(ClientThreadWorker) - obsługa przychodzących wiadomości

    '''

    def __init__(self):
        super().__init__()
        self.main_scene = QStackedWidget()
        self.login_window = LoginWindow()
        self.main_window = MainWindow()
        self.client = Client()

        # podpięcie sygnałów
        self.login_window.login_button.clicked.connect(self.login)
        self.main_window.logout_button.clicked.connect(self.logout)
        self.main_window.increase10_button.clicked.connect(self.test_info)

        # główna scena, to QStackedWidget - coś ala zbiór widżetów. Aby się pomiędzy nimi przełączać,
        # najpierw trzeba je dodać.

        self.main_scene.addWidget(self.login_window)
        self.main_scene.addWidget(self.main_window)

        self.logged = False
        self.worker = None

        self.main_scene.setFixedSize(
            self.login_window.minimumWidth(), self.login_window.minimumHeight())
        self.main_scene.show()

    def login(self):
        '''
        LOGOWANIE PODPIETE POD KLIENTA
        '''
        username = self.login_window.username.text()
        password = self.login_window.password.text()

        if username and password:
            try:
                succes, error = self.client.login(username, password)

                if not succes:
                    QMessageBox.critical(self.main_scene, "LOGOWANIE",
                                         f"Podano niepoprawne dane: {error}")
                    return

                self.main_window.username_label.setText(username)
                self.worker = ClientWorkerThread(self.client)
                self.worker.start()
                self.worker.udpate.connect(self.update_gui)
                self.logged = True

                self.main_scene.setCurrentIndex(
                    self.main_scene.currentIndex()+1)
                self.main_scene.setFixedSize(
                    self.main_window.minimumWidth(), self.main_window.minimumHeight())

            except socket.error:
                QMessageBox.critical(self.main_scene, "LOGOWANIE",
                                     "Problem z serwerem")
                return

        else:
            QMessageBox.warning(self.main_scene, "LOGOWANIE",
                                "Uzupełnij brakujące dane")

    def logout(self):
        '''
        IMPLEMENTACJA NA CHWILĘ. TO SIĘ ZMIENI
        '''
        if self.logged:
            self.worker.stop()
            self.client.logout()
            self.logged = False
            self.main_scene.setCurrentIndex(self.main_scene.currentIndex()-1)
            self.main_scene.setFixedSize(
                self.login_window.minimumWidth(), self.login_window.minimumHeight())
            self.main_window.current_auction_item_label.setText('Przedmiot: ')
            self.main_window.auction_time_label_4.setText('0')

    def test_info(self):
        if self.logged:
            m = QTraderMessage(
                "info", {"username": self.client.username, "token": self.client.token})
            self.client.ssl_socket.sendall(m.format_to_send())

    def update_gui(self, val):
        item, price= val
        label = self.main_window.current_auction_item_label.text()
        self.main_window.current_auction_item_label.setText(label+item)
        self.main_window.auction_time_label_4.setText(str(price))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    user_gui = GUI()
    sys.exit(app.exec_())
