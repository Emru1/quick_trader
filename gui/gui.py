from PyQt5.QtCore import QThread, QTimer, pyqtSignal
from functools import partial
from PyQt5.QtWidgets import QMainWindow, QApplication, QStackedWidget, QMessageBox
from PyQt5 import uic
import socket
import sys
from client.client import Client
from client.qtrader_message import QTraderMessage


class ClientWorkerThread(QThread):
    '''
    Przechwytuje wiadomości od klienta
    '''
    auction_info = pyqtSignal()
    auction_started = pyqtSignal()
    auction_ended = pyqtSignal()
    error_message = pyqtSignal()
    udpate = pyqtSignal()

    def __init__(self, client, parent=None):
        super().__init__(parent=parent)
        self.client = client

    def run(self):
        messages = self.client.listen()

        for message in messages:
            self.handle_message(message)

    def handle_message(self, message):
        '''
        Sprawdź co trzeba i rzuć odpowiednie sygnały
        '''

        if message == 'auction_started':
            self.auction_started.emit()

        elif message == 'auction_updated':
            self.udpate.emit()

        elif message == 'error_message':
            self.error_message.emit()

        elif message == 'auction_not_started_yet':
            self.auction_info.emit()

        elif message == 'auction_ended':
            self.auction_ended.emit()

    def stop(self):
        self.terminate()


class InfoWindow(QMainWindow):
    '''
    Okno informacji
    '''

    def __init__(self):
        super().__init__()
        uic.loadUi('info.ui', self)
        self.show()


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
        self.info_window = InfoWindow()
        self.client = Client()

        self.connect_buttons()

        # główna scena, to QStackedWidget - coś ala zbiór widżetów. Aby się pomiędzy nimi przełączać,
        # najpierw trzeba je dodać.

        self.main_scene.addWidget(self.login_window)
        self.main_scene.addWidget(self.main_window)
        self.main_scene.addWidget(self.info_window)

        self.timer = QTimer(self.main_window)
        self.timer.timeout.connect(self.auction_timer)

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
                success, error = self.client.login(username, password)

                if not success:
                    QMessageBox.critical(self.main_scene, "LOGOWANIE",
                                         f"Podano niepoprawne dane: {error}")
                    return

                self.main_window.username_label.setText(username)
                self.connect_signals()
                self.logged = True

                self.main_scene.setCurrentIndex(
                    1)
                self.main_scene.setFixedSize(
                    self.main_window.minimumWidth(), self.main_window.minimumHeight())
                self.client.get_info()

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
            self.main_scene.setCurrentIndex(0)
            self.main_scene.setFixedSize(
                self.login_window.minimumWidth(), self.login_window.minimumHeight())
            self.main_window.current_auction_item_label.setText('Przedmiot: ')
            self.main_window.auction_time_label_4.setText('0')

    def bet(self, price):
        if self.logged:
            self.client.bet(price)

    def connect_buttons(self):
        # podpięcie sygnałów/przyciskow
        self.login_window.login_button.clicked.connect(self.login)
        self.info_window.login_button.clicked.connect(self.logout)
        self.main_window.logout_button.clicked.connect(self.logout)
        self.main_window.increase10_button.clicked.connect(
            partial(self.bet, 10))
        self.main_window.increase50_button.clicked.connect(
            partial(self.bet, 50))
        self.main_window.increase100_button.clicked.connect(
            partial(self.bet, 100))
        self.main_window.increase500_button.clicked.connect(
            partial(self.bet, 500))
        self.main_window.increase1000_button.clicked.connect(
            partial(self.bet, 1000))

    def connect_signals(self):
        self.worker = ClientWorkerThread(self.client)
        self.worker.start()
        self.worker.udpate.connect(self.update_gui)
        self.worker.auction_started.connect(self.start_auction)
        self.worker.auction_info.connect(self.auction_not_started)
        self.worker.auction_ended.connect(self.auction_ended)
        self.worker.error_message.connect(self.info_message)

    def update_gui(self):
        self.main_window.auction_time_label_4.setText(
            str(self.client.actual_price))
        self.main_window.auction_time_label_5.setText(
            self.client.current_leader)

    def auction_timer(self):
        self.client.count -= 1
        if self.client.auction_started:

            if self.client.count == 0:
                self.client.auction_started = False
                self.main_window.auction_time_label_3.setText("0s")
                self.timer.stop()

            text = str(self.client.count / 10) + " s"
            self.main_window.auction_time_label_3.setText(text)

    def start_auction(self):
        self.timer.start(100)
        self.update_gui()

        self.main_window.current_auction_item_label.setText(
            f'PRZEDMIOT: {self.client.item_name}')
        self.main_window.current_auction_item_start_price_label.setText(
            f'CENA WYWOŁAWCZA: {self.client.actual_price}')
        # if self.main_scene.currentIndex() == 2:
        self.main_scene.setCurrentIndex(1)
        self.main_scene.setFixedSize(
            self.main_window.minimumWidth(), self.main_window.minimumHeight())


    def info_message(self):
        self.main_scene.setCurrentIndex(2)
        self.main_scene.setFixedSize(
            self.info_window.minimumWidth(), self.info_window.minimumHeight())
        self.info_window.hello_label_2.setText(
            'AKTUALNIE BRAK DOSTĘPNYCH LICYTACJI')

    def auction_not_started(self):
        self.main_scene.setCurrentIndex(2)
        self.main_scene.setFixedSize(
            self.info_window.minimumWidth(), self.info_window.minimumHeight())
        self.info_window.hello_label_2.setText(
            f'PRZEDMIOT: {self.client.item_name} \r\n DATA: {self.client.date_auction_start_time}')

    def auction_ended(self):
        QMessageBox.information(
            self.main_scene, 'KONIEC', f'PRZEDMIOT: {self.client.item_name} \r\n CENA: {self.client.actual_price} \r\n ZWYCIĘZCA: {self.client.current_leader}')
        self.timer.stop()
        self.client.get_info()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    user_gui = GUI()
    sys.exit(app.exec_())
