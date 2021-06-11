import sys

SETTING_KEYS = ['ip', 'port', 'dbpath', 'tls_cert', 'tls_key']

GLOBAL_CONFIG = None


class Config:
    """
    Klasa konfiguracji, jest to singleton
    """
    def __init__(self, path='./config'):
        """
        Inicjalizacja i parsowanie pliku konfiguracyjnego

        :param path: Ścieżka do pliku konfiguracyjnego, jeśli niepodana,
                     to zostanie użyta domyślna ścieżka './config'
        """
        self.port = '55555'
        self.ip = '0.0.0.0'
        self.dbpath = './db.sqlite3'
        self.tls_cert = './tls.cert'
        self.tls_key = './tls.key'
        # Więcej ustawień

        try:
            config_file = open(path, 'r')
        except IOError:
            print("Unable to open file '{}'".format(path))
            print("Using default config.")
        else:
            self._parse_file(config_file)
            config_file.close()

        global GLOBAL_CONFIG
        GLOBAL_CONFIG = self

    def _parse_file(self, config_file):
        """
        Prywatna metoda parsująca plik konfiguracyjny

        :param config_file: Ścieżka do pliku
        """
        for linex in config_file:
            line = linex.rstrip()
            key = line.split(' ')[0]
            value = line.split(' ')[1]

            if key not in SETTING_KEYS:
                print('Config parsing error: wrong file line {}'.format(line))
                continue
            setattr(self, key, value)

    def print_config(self):
        """
        Funkcja wypisująca aktualną konfigurację
        """

        print("\n\nCurrent configuration:")

        line_len = 2
        for key in SETTING_KEYS:
            if len(key) > line_len:
                line_len = len(key)
        line_len += 4

        for key in SETTING_KEYS:
            value = getattr(self, key)
            print(str(key).ljust(line_len, ' '), ' -  ', value)

        print("End of configuration listing\n\n")
