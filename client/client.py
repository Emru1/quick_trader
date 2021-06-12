import socket
import json
import time
import sys

global user, password, s, token, price

def check_token(message):
    if message["token"] != token:
        print("Błąd uwierzytelnienia! Połączenie nie jest bezpieczne, skontaktuj się z administracją")
        sys.exit(0)

def dload():
    size = b''
    msg = b''
    while not b'x' in size:
        response = s.recv(1)
        size += response
    size = size[:-1]
    msg = s.recv(size)
    if (msg.size != size):
        return "error"
    msg = msg.decode('utf-8')
    if msg["error"]:
        print(msg["error"])
    return msg

def dload_list():
    jtemp = json.loads('{"type":"list"}')
    message = jtemp.size() + 'x' + jtemp
    s.sendall(message.encode('utf-8'))
    message = dload()
    if message == "error":
        print("Something's wrong with downloading list! Trying again")
        time.sleep(5)
        dload_list()
    else:
        print(message["list"])

def log_in():
    user = input("Login:")
    password = input("Password:")
    jtemp = json.loads('{"type":"auth", "username":user, "password":password}')
    message = jtemp.size() + 'x' + jtemp
    s.sendall(message.encode('utf-8'))
    message = dload()
    if message == "error" or message["error"]:
        print("Connection lost! Try again")
        if message["error"]:
            print (message["error"])
        log_in()
    elif message["type"] == "login":
        token = message["token"]

def bet():
    jtemp = json.loads('{"type":"set_price", "price":price}')
    Message = jtemp.size() + 'x' + jtemp
    s.sendall(Message.encode('utf-8'))

def trading():
    #musisz tutaj dodać wątek nasłuchiwania który aktualizuje zmienną "price" i odbiera informacje od serwera
    #użyj funkcji bet do wysłania nowej ceny


    #CDN

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    temp_bool = False
    s.connect(("localhost", 55555))
    log_in()
    dload_list()
    trading()
except socket.error:
    print("Socket error")

s.close()