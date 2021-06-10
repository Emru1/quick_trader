from PyQt5.QtWidgets import QMainWindow, QApplication, QStackedWidget
from PyQt5 import uic
import sys
import time
from threading import Thread

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

        #podpięcie sygnałów 
        self.login_window.login_button.clicked.connect(self.login)
        self.main_window.logout_button.clicked.connect(self.logout)

        #główna scena, to QStackedWidget - coś ala zbiór widżetów. Aby się pomiędzy nimi przełączać,
        #najpierw trzeba je dodać.

        self.main_scene.addWidget(self.login_window)
        self.main_scene.addWidget(self.main_window)
        
        self.username = None
        self.logged = False

        self.main_scene.setFixedSize(self.login_window.minimumWidth(), self.login_window.minimumHeight())
        self.main_scene.show()
    
    def login(self):
        '''
        IMPLEMENTACJA NA CHWILĘ. TO SIĘ ZMIENI
        '''
        username = self.login_window.username.text()

        if username:
            self.main_scene.setCurrentIndex(self.main_scene.currentIndex()+1)
            self.main_window.username_label.setText(username)
            self.username = username
            self.logged = True
            self.main_scene.setFixedSize(self.main_window.minimumWidth(), self.main_window.minimumHeight())

    def logout(self):
        '''
        IMPLEMENTACJA NA CHWILĘ. TO SIĘ ZMIENI
        '''
        if self.logged:
            self.main_scene.setCurrentIndex(self.main_scene.currentIndex()-1)
            print(self.main_scene.currentWidget)
            self.main_scene.setFixedSize(self.login_window.minimumWidth(), self.login_window.minimumHeight())

if __name__ == '__main__':
    app = QApplication(sys.argv)
    user_gui = GUI()
    sys.exit(app.exec_())