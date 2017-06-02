# -*- coding: utf-8 -*-

import time
import socket
import argparse
import select
import errno

from commands import NOSQL_COMMANDS, init_database
from constants import *

def __parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", "-i", help="Server listening IP address [default: 127.0.01]", default="127.0.0.1")
    parser.add_argument("--port", "-p", help="Server listening port [default: 9527]", type=int, default=9527)
    parser.add_argument("--enauth", "-e", help="Enable auth password", action="store_true")
    parser.add_argument("--authpwd", "-a", help="Set server-end auth password", default=None)
    parser.add_argument("--timeout", "-t", help="Set timeout to check client connections", default=10)

    return parser.parse_args()

def parse_message(data):
    if not data:
        return None, None, None, None, None

    try:
        values = list(map(lambda val: val.strip(), data.strip().split(';')))
    except Exception as e:
        print("Invalid input!, Excpted: command; [key]; [value]; [valuetype]; [dbid]")
        return None, None, None, None, None

    if len(values) == 4:
        return values[0].lower(), values[1], values[2], values[3].lower(), -1
    elif len(values) == 2:
        return values[0].lower(), values[1], None, None, -1
    elif len(values) == 3:
        return values[0].lower(), values[1], values[2], VT_STRING, -1
    elif len(values) >= 5:
        return values[0].lower(), values[1], values[2], values[3], int(values[4])
    elif len(values) == 1:
        return values[0].lower(), None, None, None, -1

    print("Invalid input!, Excpted: command; [key]; [value]; [valuetype]; [dbid]")
    return None, None, None, None, None

def process_client(client):
    data = ""
    while True:
        try:
            d = client["conn"].recv(4096).decode("utf-8")
            if not d and not data:
                return False
            data += d
        except socket.error as e:
            if e.errno == errno.EAGAIN:
                break
            else:
                print(e)
                return False

    print("recv data [{0}]".format(data))
    command, key, value, valuetype, dbid = parse_message(data)

    if command not in NOSQL_COMMANDS:
        client["message"] = NOSQL_ERRMSGS[ERR_INVALIDCMD]
        return True

    print("command = [{0}, {1}, {2}, {3}, {4}]".format(command, key, value, valuetype, dbid))

    if command in (COMMAND_SET, COMMAND_LPUSH):
        flag, code, response = NOSQL_COMMANDS[command]["func"](key, value, valuetype, dbid)
    elif command in (COMMAND_GET, COMMAND_LPOP, COMMAND_DELETE):
        flag, code, response = NOSQL_COMMANDS[command]["func"](key, dbid)
    elif command in (COMMAND_SELECT, COMMAND_KEYS):
        flag, code, response = NOSQL_COMMANDS[command]["func"](dbid)
    elif command in (COMMAND_AUTH):
        flag, code, response = NOSQL_COMMANDS[command]["func"](key)

    client["message"] = NOSQL_ERRMSGS[code]
    client["response"] = response

    return True

def main():
    args = __parse_args()

    socks = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socks.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
    socks.bind((args.ip, args.port))
    socks.listen(1024)
    socks.setblocking(False)

    # epoll register listen socket fd
    epfd = select.epoll()
    epfd.register(socks.fileno(), select.EPOLLIN)

    # init database
    init_database(args.enauth, args.authpwd)

    clients = {}
    while 1:
        events = epfd.poll()
        if not events:
            continue

        for fd, event in events:
            if fd == socks.fileno():
                conn, addr = socks.accept()
                conn.setblocking(False)

                epfd.register(conn.fileno(), select.EPOLLIN)
                clients[conn.fileno()] = {}
                clients[conn.fileno()]["conn"] = conn
                clients[conn.fileno()]["message"] = ""
                clients[conn.fileno()]["response"] = None
                print("{} new connection from {}".format(time.strftime(("%Y/%m/%d %H:%M:%S INFO"), time.localtime()), addr))
            elif event & select.EPOLLIN:
                client = clients[fd]
                if process_client(client):
                    # continue to process send response
                    epfd.modify(fd, select.EPOLLOUT)
                else:
                    epfd.unregister(fd)
                    clients[fd]["conn"].close()
                    del clients[fd]
            elif event & select.EPOLLOUT:
                client = clients[fd]
                data = "message: {0}\nresponse: {1}".format(client["message"], client["response"])

                data = bytearray(data, "utf-8")
                sendlen = 0
                while 1:
                    sendlen += client["conn"].send(data[sendlen:])
                    if sendlen == len(data):
                        break

                # continue to read next request
                epfd.modify(fd, select.EPOLLIN)
            elif event & select.EPOLLHUP:
                epfd.unregister(fd)
                clients[fd]["conn"].close()
                del clients[fd]

if __name__ == "__main__":
    main()


