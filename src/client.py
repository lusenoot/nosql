# -*- coding: utf-8 -*-

import socket
import argparse
import unicodedata
import sys

def __parse_args():
	parser = argparse.ArgumentParser()

	parser.add_argument("--ip", help="Server listening IP address [default: 127.0.01]", default="127.0.0.1")
	parser.add_argument("--port", help="Server listening port [default: 9527]", type=int, default=9527)

	parser.add_argument("--cmd", action="store", default="get", choices=["put", "get", "delete", "select", "keys"], help="Operation")
	parser.add_argument("--key", action="store", help="Key")
	parser.add_argument("--value", action="store", help="Value")
	parser.add_argument("--dbid", action="store", default=0, help="dbid")

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

def main():
	args = __parse_args()

	valuetype = "string"
	if args.value is not None:
		if is_number(args.value):
			valuetype = "number"

	if args.key and args.value and args.cmd in ("put"):
		data = u"{0}; {1}; {2}; {3}; {4}".format(args.cmd, args.key, args.value, valuetype, args.dbid)
	elif args.key and args.cmd in ("get", "delete"):
		data = u"{0}; {1}; {2}".format(args.cmd, args.key, args.dbid)
	elif args.cmd in ("select", "keys"):
		data = u"{0}; {1}".format(args.cmd, args.dbid)
	else:
		sys.exit(1)

	socks = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	socks.connect((args.ip, args.port))
	socks.send(data.encode("utf-8"))

	data = socks.recv(4096)
	print data.decode("utf-8")

if __name__ == '__main__':
	main()


