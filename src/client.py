# -*- coding: utf-8 -*-

import socket
import argparse
import unicodedata
import sys
import readline # for cmdline mode to delete characters

from constants import *

parser = None

def is_number(value):
    try:
        float(value)
        return True
    except ValueError:
        pass

    try:
        unicodedata.numeric(value)
        return True
    except (TypeError, ValueError):
        pass

    return False

def __parse_dbid(kvargs, limited):
    dbid = 0
    try:
        if len(kvargs) >= limited:
            dbid = int(kvargs[limited - 1])
    except:
        dbid = 0

    return dbid

def process_args(args):
    data = None

    if args.command in (COMMAND_SET, COMMAND_LPUSH):
        if len(args.kvargs) < 2:
            print("params error, need Key Value at least")
            return None

        valuetype = VT_STRING
        if args.kvargs[1] is not None:
            if is_number(args.kvargs[1]):
                valuetype = VT_NUMBER
            elif "," in args.kvargs[1]:
                valuetype = VT_LIST

        if args.command == COMMAND_LPUSH:
            valuetype = VT_LIST

        dbid = __parse_dbid(args.kvargs, 3)
        data = u"{0}; {1}; {2}; {3}; {4}".format(args.command, args.kvargs[0], args.kvargs[1], valuetype, dbid)
    elif args.command in (COMMAND_GET, COMMAND_LPOP, COMMAND_DELETE):
        if len(args.kvargs) < 1:
            print("params error, need Key at least")
            return None

        dbid = __parse_dbid(args.kvargs, 2)
        data = u"{0}; {1}; {2}".format(args.command, args.kvargs[0], dbid)
    elif args.command in (COMMAND_SELECT, COMMAND_KEYS):
        dbid = __parse_dbid(args.kvargs, 1)
        data = u"{0}; {1}".format(args.command, dbid)
    elif args.command in (COMMAND_AUTH):
        if len(args.kvargs) < 1:
            print("params error, no password input!!!")
            return None
        data = u"{0}; {1}".format(args.command, args.kvargs[0])
    else:
        print("Invalid command")

    return data

def send_command(args, data):
    socks = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socks.connect((args.ip, args.port))
    socks.send(data.encode("utf-8"))

    data = socks.recv(4096)
    print data.decode("utf-8")
    socks.close()

def process_cmdline(args):
    while 1:
        args.command = None
        args.kvargs = None
        inputs = raw_input("cmdline> ")
        commands = map(lambda val: val.strip(), inputs.strip().split())
        if len(commands) == 0:
            continue

        args.command = commands.pop(0)
        if args.command == "q" or args.command == "quit" or args.command == "exit" or args.command == "bye":
            sys.exit(0)
        elif args.command == "help" or args.command == "?":
            parser.print_help()
            continue

        args.kvargs = commands

        data = process_args(args)
        if data:
            send_command(args, data)

def __parse_args():
    global parser
    parser = argparse.ArgumentParser()

    parser.add_argument("--ip", help="Server listening IP address [default: 127.0.01]", default="127.0.0.1")
    parser.add_argument("--port", help="Server listening port [default: 9527]", type=int, default=9527)
    parser.add_argument("--auth", help="Set password for connected database [default: None]", default=None)

    subparsers = parser.add_subparsers(dest="command", metavar="command")
    subparsers.required = True

    set_parser = subparsers.add_parser(COMMAND_SET, help="set Key-Value to db [dbid = 0]")
    set_parser.add_argument("kvargs", nargs="+", metavar="kvargs")

    get_parser = subparsers.add_parser(COMMAND_GET, help="get Value from db by Key [dbid = 0]")
    get_parser.add_argument("kvargs", nargs="+", metavar="kvargs")

    lpush_parser = subparsers.add_parser(COMMAND_LPUSH,
            help="set Key-Value(Value splited by \",\") to db [dbid = 0]")
    lpush_parser.add_argument("kvargs", nargs="+", metavar="kvargs")

    lpop_parser = subparsers.add_parser(COMMAND_LPOP,
            help="get first Value to list by Key [dbid = 0]")
    lpop_parser.add_argument("kvargs", nargs="+", metavar="kvargs")

    delete_parser = subparsers.add_parser(COMMAND_DELETE, help="delete Key-Value from db by Key [dbid = 0]")
    delete_parser.add_argument("kvargs", nargs="+", metavar="kvargs")

    select_parser = subparsers.add_parser(COMMAND_SELECT, help="switch db by dbid")
    select_parser.add_argument("kvargs", nargs="?", metavar="kvargs", help="user dbid")

    keys_parser = subparsers.add_parser(COMMAND_KEYS, help="list all keys by dbid")
    keys_parser.add_argument("kvargs", nargs="?", metavar="kvargs", help="user dbid")

    auth_parser = subparsers.add_parser(COMMAND_AUTH, help="set password for connected database")
    auth_parser.add_argument("kvargs", nargs="?", metavar="kvargs", help="set password")

    cmdline_parser = subparsers.add_parser("cmdline", help="Start cmdline mode")
    cmdline_parser.add_argument("kvargs", nargs="?", metavar="kvargs")

    return parser.parse_args()

def main():
    args = __parse_args()

    if not args.command and args.command != "cmdline":
        data = process_args(args)
    elif args.command == "cmdline":
        process_cmdline(args)
    else:
        sys.exit(1)

    if not data:
        send_command(args, data)

if __name__ == '__main__':
    main()


