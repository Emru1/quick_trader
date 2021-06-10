import socket
import json
import time

def dload():
    size = b''
    msg = b''
    while not b'\0' in size:
        response = s.recv(1)
        size += response
    size = size[:-1]
    msg = s.recv(size)
    if (msg.size != size):
        return "error"
    return msg.decode('utf-8')[:-4]


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    temp_bool = False
    s.connect(("localhost", 54321))
    while not temp_bool:
        user = input("Login:")
        password = input("Password:")
        jtemp = json.loads('{"type":"login", "data":password, "who":user}')
        Message = jtemp.size() + '\0' + jtemp
        s.sendall(Message.encode('utf-8'))
        Message = dload()
        if Message == "error":
            print("Connection lost! Try again")
            continue
        if Message["type"]== "login":
            if (Message["data"]):
                login_istrue = True

    temp_bool = False
    while not temp_bool:
        jtemp = json.loads('{"type":"ask", "data":"dload_trades", "who":user}')
        Message = jtemp.size() + '\0' + jtemp
        s.sendall(Message.encode('utf-8'))
        Message = dload()
        if Message == "error":
            print("Something's wrong with downloading list! Trying again")
            time.sleep(5)
            continue
        print(Message["data"])

    temp_bool = False
    while not temp_bool:
        trade_id = input("Select trade ID:")
        jtemp = json.loads('{"type":"join_trade", "data":"trade_id", "who":user}')
        Message = jtemp.size() + '\0' + jtemp
        s.sendall(Message.encode('utf-8'))
        Message = dload()
        if Message == "error":
            print("Something's wrong! Try again")
            continue
        temp_bool = True





except socket.error:
    print("error")

s.close()