from psutil import disk_partitions, disk_usage
import os, time, functools, pickle
from socket import *
from datetime import datetime

server_host = "your_server_ip"
server_port = 4488

def coroutine(gen_func):

    @functools.wraps(gen_func)
    def start(*args, **kwargs):
        cr = gen_func(*args, **kwargs)
        cr.send(None)
        return cr
    return start

@coroutine
def send_log():
    while True:
        log_line = (yield)
        log_line_bytes = pickle.dumps(log_line)
        socket_to_server = socket(AF_INET, SOCK_STREAM)
        socket_to_server.connect((server_host, server_port))
        print("Connect to server {} {}".format(server_host, server_port))
        socket_to_server.send(log_line_bytes)
        print("Connection close")
        socket_to_server.close()

def get_free_space():
    disks = disk_partitions()
    disk_free_space = {}
    for i in range(len(disks)):
        disk_letter = str(disks[i])[18:20]
        disk_free_space[disk_letter] = int(disk_usage(disk_letter).free/(1024*1024*1024))
    return disk_free_space

def write_log(*args):
    file, mode, sender = args
    while True:
        log_file = open(file, mode)
        log_line = str(get_free_space())
        log_file.write(str(datetime.now()) + log_line + "\n")
        log_file.close()
        sender.send(log_line)
        time.sleep(600)
        continue

write_log(*["test_log.txt", "a", send_log()])