# -*- coding: utf-8 -*-

import socket
import argparse
import unicodedata
import sys

def __parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("--ip", help="Server listening IP address [default: 127.0.01]", default="127.0.0.1")
    parser.add_argument("--port", help="Server listening port [default: 9527]", type=int, default=9527)

    subparsers = parser.add_subparsers(dest="command", metavar="command")
    subparsers.required = True

    set_parser = subparsers.add_parser("set", help="set Key-Value to db [dbid = 0]")
    set_parser.add_argument("kvargs", nargs="+", metavar="kvargs", help="kv params splited by \";\"")

    plist_parser = subparsers.add_parser("plist",
            help="set Key-Value(Value splited by \",\") to db [dbid = 0]")
    plist_parser.add_argument("kvargs", nargs="+", metavar="kvargs", help="kv params splited by \";\"")

    get_parser = subparsers.add_parser("get", help="get Value from db by Key [dbid = 0]")
    get_parser.add_argument("kvargs", nargs="+", metavar="kvargs", help="key params splited by \";\"")

    delete_parser = subparsers.add_parser("delete", help="delete Key-Value from db by Key [dbid = 0]")
    delete_parser.add_argument("kvargs", nargs="+", metavar="kvargs", help="key params splited by \";\"")

    select_parser = subparsers.add_parser("select", help="switch db by dbid")
    select_parser.add_argument("kvargs", nargs="?", metavar="kvargs", help="user dbid")

    keys_parser = subparsers.add_parser("keys", help="list all keys by dbid")
    keys_parser.add_argument("kvargs", nargs="?", metavar="kvargs", help="user dbid")

    return parser.parse_args()

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


def main():
    args = __parse_args()

    if args.command in ("set", "plist"):
        if len(args.kvargs) < 2:
            print("params error, need Key Value at least")
            sys.exit(1)

        valuetype = "string"
        if args.kvargs[1] is not None:
            if is_number(args.kvargs[1]):
                valuetype = "number"
            elif "," in args.kvargs[1]:
                valuetype = "list"

        if args.command == "plist":
            valuetype = "list"

        dbid = __parse_dbid(args.kvargs, 3)
        data = u"{0}; {1}; {2}; {3}; {4}".format(args.command, args.kvargs[0], args.kvargs[1], valuetype, dbid)
    elif args.command in ("get", "delete"):
        if len(args.kvargs) < 1:
            print("params error, need Key at least")
            sys.exit(1)

        dbid = __parse_dbid(args.kvargs, 2)
        data = u"{0}; {1}; {2}".format(args.command, args.kvargs[0], dbid)
    elif args.command in ("select", "keys"):
        dbid = __parse_dbid(args.kvargs, 1)
        data = u"{0}; {1}".format(args.command, dbid)
    else:
        sys.exit(1)

    socks = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socks.connect((args.ip, args.port))
    socks.send(data.encode("utf-8"))

    data = socks.recv(4096)
    print data.decode("utf-8")

    socks.close()

if __name__ == '__main__':
    main()


