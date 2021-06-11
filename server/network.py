import sys
import ssl
import socket
import select


class Server:
    def __init__(self, inqueue, outqueue):
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
        for fd, event in self.poll.poll():
            if event & (select.POLLHUP | select.POLLERR | select.POLLNVAL):
                self.poll.uregister(fd)
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
                self.inqueue.put({'data': data, 'fd': fd})

    def __del__(self):
        self.ssocket.close()
        self.serversocket.close()
        for fd in self.clients:
            self.poll.unregister(fd)
        del self.clients


class Client:
    def __init__(self, sock, address):
        self.sock = sock
        self.address = address
        self.sock.setblocking(False)
        self._zero_all()

    def _zero_all(self):
        self.data = b''
        self.size_header = b''
        self.size_received = False
        self.size = 0
        self.received = 0
        self.ready = False

    def __del__(self):
        self.sock.close()

    def receive_data(self):
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
                return ret
        except ssl.SSLWantReadError:
            print('Receive error from {}'.format(self.address))
            self._zero_all()
