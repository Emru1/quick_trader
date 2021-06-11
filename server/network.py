import sys
import ssl
import socket
import select


class Server:
    def __init__(self):
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
        except:
            print('Error with creating TLS context')
            sys.exit(1)

        self.poll = select.poll()
        self.poll.register(self.ssocket, select.POLLIN)

        self.clients = {}

    def handle_network(self):
        for fd, event in self.poll.poll():
            if event & (select.POLLHUP | select.POLLERR | select.POLLNVAL):
                poll.uregister(fd)
                del self.clients[fd]

            elif fd == self.ssocket.fileno():
                client_sock, addr = self.ssocket.accept()
                print(type(client_sock))
                client = Client(client_sock, addr)
                fd = client_sock.fileno()
                self.clients[fd] = client
                self.poll.register(fd, select.POLLIN)
                print('Connection from {} estabilished'.format(addr))

            elif event & select.POLLIN:
                client = self.clients[fd]
                client.receive_data()

    def __del__(self):
        pass


class Client:
    def __init__(self, sock, address):
        self.sock = sock
        self.address = address
        self.sock.setblocking(False)

    def __del__(self):
        self.sock.close()

    def receive_data(self):
        data = b''
        while b'x' not in data:
            data += self.sock.recv(1)
            if not data:
                return b''
        try:
            data = data[:-1]
            print(data)
            data_len = int(data)
        except ValueError:
            print('Connection from {} sent wrong packet size: {}'.format(
                self.address, data))
            return {'type': 'error', 'message': 'Wrong packet size header'}

        data = b''
        received = 0
        while received < data_len:
            print(data)
            data += self.sock.recv(data_len - received)
            received += len(data)

        print(data)
        return data
