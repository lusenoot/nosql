# -*- coding: utf-8 -*-

import time
import socket
import argparse

from commands import NOSQL_COMMANDS
from constants import *

def __parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", "-i", help="Server listening IP address [default: 127.0.01]", default="127.0.0.1")
    parser.add_argument("--port", "-p", help="Server listening port [default: 9527]", type=int, default=9527)

    return parser.parse_args()

def parse_message(data):
    if not data:
        return None, None, None, None, None

    try:
        values = map(lambda val: val.strip(), data.strip().split(';'))
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

def main():
    args = __parse_args()

    socks = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socks.bind((args.ip, args.port))
    socks.listen(1024)
    socks.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)

    while 1:
        conn, addr = socks.accept()
        print("{} new connection from {}".format(time.strftime(("%Y/%m/%d %H:%M:%S INFO"), time.localtime()), addr))

        data = conn.recv(4096).decode("utf-8")
        print("recv data [{0}]".format(data))
        command, key, value, valuetype, dbid = parse_message(data)

        if command not in NOSQL_COMMANDS:
            print(NOSQL_ERRMSGS[ERR_INVALIDCMD])

        print("command = [{0}, {1}, {2}, {3}, {4}]".format(command, key, value, valuetype, dbid))

        if command in (COMMAND_PUT, COMMAND_PLIST):
            flag, code, response = NOSQL_COMMANDS[command]["func"](key, value, valuetype, dbid)
        elif command in (COMMAND_GET, COMMAND_DELETE):
            flag, code, response = NOSQL_COMMANDS[command]["func"](key, dbid)
        elif command in (COMMAND_SELECT, COMMAND_KEYS):
            flag, code, response = NOSQL_COMMANDS[command]["func"](dbid)

        data = "message: {0}\nresponse: {1}".format(NOSQL_ERRMSGS[code], response)
        conn.sendall(bytearray(data, 'utf-8'))
        conn.close()
        print(data)

if __name__ == "__main__":
    main()


