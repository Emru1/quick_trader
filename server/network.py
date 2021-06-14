import sys
import ssl
import socket
import select
import time
import queue


class Server:
    """
    Obiekt serwera, obsługuje on zdarzeniowo podpiętych klientów
    oraz zarządza TLSem
    """
    def __init__(self, inqueue: queue.Queue, outqueue: queue.Queue):
        """
        Metoda ta inicjalizuje gniazdo serwera, a także kontekst TLS
        Przyporządkówuje także kolejki wejścia i wyjścia

        :param: inqueue(queue.Queue) - kolejka wejściowa, są to pakiety
        przychodzące od użytkowników
        :param: outqueue(queue.Queue) - kolejka wyjściowa, są to pakiety
        danych które zostaną wysłane do użytkowników
        """

        from config import GLOBAL_CONFIG
        print('Opening server socket on {}'.format(GLOBAL_CONFIG.ip + ':' +
                                                   GLOBAL_CONFIG.port))
        try:
            self.serversocket = socket.socket(socket.AF_INET,
                                              socket.SOCK_STREAM)
            self.serversocket.bind((GLOBAL_CONFIG.ip, int(GLOBAL_CONFIG.port)))
            self.serversocket.listen(128)
        except socket.error:
            print('Server initialization error')
            sys.exit(1)
        try:
            self.context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            self.context.load_cert_chain(GLOBAL_CONFIG.tls_cert,
                                         GLOBAL_CONFIG.tls_key)
            self.ssocket = self.context.wrap_socket(self.serversocket,
                                                    server_side=True)
        except ssl.SSLError:
            print('Error with creating TLS context')
            sys.exit(1)
        except IOError:
            print('Error with TLS IO')
            sys.exit(1)

        self.poll = select.poll()
        self.poll.register(self.ssocket, select.POLLIN)

        self.inqueue = inqueue
        self.outqueue = outqueue

        self.clients = {}

    def handle_network(self):
        """
        Obsługa sieci, najpierw odbiera wszystkie dane i wrzuca je do outqueue
        po czym wysyła dane z inqueue
        """
        for fd, event in self.poll.poll(10):
            print(fd, event)
            if event & (select.POLLHUP | select.POLLERR | select.POLLNVAL):
                self.poll.unregister(self.clients[fd].sock)
                del self.clients[fd]

            elif fd == self.ssocket.fileno():
                client_sock, addr = self.ssocket.accept()
                client = Client(client_sock, addr)
                fd = client_sock.fileno()
                self.clients[fd] = client
                self.poll.register(fd, select.POLLIN)
                print('Connection from {} estabilished'.format(addr))

            elif event & select.POLLIN:
                client = self.clients[fd]
                data = client.receive_data()
                if data:
                    self.inqueue.put({'data': data, 'fd': fd})

        while not self.outqueue.empty():
            pkg = self.outqueue.get()
            data = pkg['data']
            print('Wiadomosc do wyslania:', data)
            fd = pkg['fd']
            if fd not in self.clients:
                continue
            client = self.clients[fd]
            client.send(data)

    def run(self):
        """
        Nieskończona pętla części sieciowej
        """
        while True:
            self.handle_network()

    def __del__(self):
        self.ssocket.close()
        self.serversocket.close()
        for fd in self.clients:
            self.poll.unregister(fd)
        del self.clients


class Client:
    """
    Klasa ta reprezentuje klienta podłączonego do serwera
    Obsługuje ona wymianę danych
    """
    def __init__(self, sock: ssl.SSLSocket, address: (str, int)):
        """
        Inicjalizacja, przyjmuje gniazdo TLSowe oraz adres klienta

        :param: sock(ssl.SSLSocket) - gniazdo klienta
        :param: address((str,int)) - krotka z adresem klienta
        """
        print(type(sock))
        print(type(address))
        print(address)
        self.sock = sock
        self.address = address
        self.sock.setblocking(False)
        self._zero_all()

    def _zero_all(self):
        """
        Czyszczenie danych tymczasowych służących do kontroli odbierania danych
        """
        self.data = b''
        self.size_header = b''
        self.size_received = False
        self.size = 0
        self.received = 0
        self.ready = False

    def __del__(self):
        self.sock.close()

    def send(self, data: str):
        """
        Metoda wysyłająca dane do klienta

        :param: data(str) - JSON wysyłany do klienta
        """
        length = str(len(data)).encode('utf-8')
        data = str(data).encode('utf-8')
        to_send = length + b'x' + data
        self.sock.sendall(to_send)

    def receive_data(self):
        """
        Metoda odbierająca dane od klienta, używa flag i buforów by móc
        swobodnie odbierać dane w wielu turach
        """
        try:
            if not self.size_received:
                while True:
                    data = self.sock.recv(1)
                    if not data:
                        return
                    if b'x' in data:
                        self.size_received = True
                        break
                    sdata = data.decode('utf-8')
                    if sdata not in '0123456789':
                        self._zero_all()
                        return
                    self.size_header += data
                if self.size_received:
                    try:
                        self.size = int(self.size_header)
                    except ValueError:
                        self._zero_all()
                        return

            if self.size_received:
                while True:
                    data = self.sock.recv(self.size - self.received)
                    data_len = len(data)
                    if not data:
                        break
                    self.data += data
                    self.received += data_len
                    if self.received == self.size:
                        self.ready = True
                        break

            if self.ready:
                ret = bytes(self.data)
                self._zero_all()
                print('Received data packet from {}'.format(self.address))
                return ret
        except ssl.SSLWantReadError:
            print('Receive error from {}'.format(self.address))
            self._zero_all()
