from socket import *
import pickle, functools, requests
from datetime import datetime

def coroutine(gen_func):

    @functools.wraps(gen_func)
    def start(*args, **kwargs):
        cr = gen_func(*args, **kwargs)
        cr.send(None)
        return cr
    return start

token = "your_token"
chat_id = "your_chat_id"

@coroutine
def send_telegram():
    while True:
        text = (yield)
        url = "https://api.telegram.org/bot{}/sendMessage?chat_id={}&text={}".format(token, chat_id, text)
        requests.request("get", url)

@coroutine
def write_log():
    while True:
        log_line = (yield)
        log_file = open("server_log.txt", "a")
        log_file.write(str(datetime.now()) + log_line + "\n")
        log_file.close()

def str_to_dict(log_line):
    line = log_line.replace("'", " ")
    line = line.replace("{", " ")
    line = line.replace("}", " ")
    lst = line.split(",")
    disks = {}
    for i in range(len(lst)):
        disk = lst[i].split(":")[0].strip()
        space = lst[i].split(":")[2].strip()
        disks[disk] = int(space)
    return disks

@coroutine
def check_free_space(target):
    while True:
        log_line = (yield)
        disks = str_to_dict(log_line)
        for key, value in disks.items():
            if value < 20:
                text = "on disk {} free volume less than 20Gb".format(key)
                target.send(text)

@coroutine
def dispenser(targets):
    while True:
        log_line = (yield)
        for target in targets:
            target.send(log_line)

server_host = ""
server_port = 4488

server_socket = socket(AF_INET, SOCK_STREAM)
server_socket.bind((server_host, server_port))
server_socket.listen(1)

def run_server(disp):
    while True:
        connection, address = server_socket.accept()
        print("Server connected with {}".format(address))
        while True:
            bytes_line = connection.recv(1024)
            if not bytes_line:
                break
            log_line = pickle.loads(bytes_line)
            disp.send(log_line)
        print("Connection with {} close".format(address))
        connection.close()

run_server(dispenser([check_free_space(send_telegram()), write_log()]))
