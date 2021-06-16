import sys
sys.path.append('\quick_trader\client')

from PyQt5.QtCore import QThread
from PyQt5.QtWidgets import QMainWindow, QApplication, QStackedWidget, QMessageBox
from PyQt5 import uic
import time
from threading import Thread
from client import Client

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

    '''
    def __init__(self):
        super().__init__()
        self.main_scene = QStackedWidget()
        self.login_window = LoginWindow()
        self.main_window = MainWindow()
        self.client = Client()

        #podpięcie sygnałów 
        self.login_window.login_button.clicked.connect(self.login)
        self.main_window.logout_button.clicked.connect(self.logout)

        #główna scena, to QStackedWidget - coś ala zbiór widżetów. Aby się pomiędzy nimi przełączać,
        #najpierw trzeba je dodać.

        self.main_scene.addWidget(self.login_window)
        self.main_scene.addWidget(self.main_window)
        
        self.logged = False

        self.main_scene.setFixedSize(self.login_window.minimumWidth(), self.login_window.minimumHeight())
        self.main_scene.show()
    
    def login(self):
        '''
        IMPLEMENTACJA NA CHWILĘ. TO SIĘ ZMIENI
        '''
        username = self.login_window.username.text()
        password = self.login_window.password.text()

        if username and password:
            succes, error = self.client.login(username, password)
            
            if not succes:
                QMessageBox.critical(self.main_scene, "LOGOWANIE",
                                f"Podano niepoprawne dane: {error}")
                return 
            
            self.main_window.username_label.setText(username)
            self.logged = True
            self.main_scene.setCurrentIndex(self.main_scene.currentIndex()+1)
            self.main_scene.setFixedSize(self.main_window.minimumWidth(), self.main_window.minimumHeight())
        
        else:
            QMessageBox.warning(self.main_scene, "LOGOWANIE",
                                "Uzupełnij brakujące dane")
    def logout(self):
        '''
        IMPLEMENTACJA NA CHWILĘ. TO SIĘ ZMIENI
        '''
        if self.logged:
            self.client.logout()
            self.main_scene.setCurrentIndex(self.main_scene.currentIndex()-1)
            self.main_scene.setFixedSize(self.login_window.minimumWidth(), self.login_window.minimumHeight())

if __name__ == '__main__':
    app = QApplication(sys.argv)
    user_gui = GUI()
    sys.exit(app.exec_())
