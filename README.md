Pierwsze uruchomienie:
GUI wymaga PyQT i innych bibliotek, które trzeba doinstalować.
Aby nie robić syfu, polecam stworzyć wirtualne środowisko i doinstalować, co trzeba.

1. Stwórz wirtualne środowisko
2. Aktywuj środowisko
3. pip install -r requirements_freeze
4. Dodaj katalog z wirtualnym środowiskiem do .gitignore

Kolejne uruchomienia:
1. Aktywuj środowisko
2. Działaj

Serwer:
przygotowanie:
1. Stwórz wirtualne środowisko Pythona 3.9 w katalogu server
2. Aktywuj je `source venv/bin/activate`
3. `pip install -r requirements.txt`
uruchomienie:
1. Aktywuj środowisko
2. wykonaj w katalogu serwer `python3.9 main.py`