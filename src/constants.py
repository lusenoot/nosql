# -*- coding: utf-8 -*-

COMMAND_PUT = "put"
COMMAND_PLIST = "plist"
COMMAND_GET = "get"
COMMAND_DELETE = "delete"
COMMAND_SELECT = "select"
COMMAND_KEYS = "keys"

VT_NUMBER = "number"
VT_STRING = "string"
VT_LIST = "list"

SUCCESS = 0
ERR_NODATABASE = 1
ERR_INVALIDCMD = 2
ERR_INVALIDKEY = 3
ERR_INVALIDVALUE = 4
ERR_NOKEY = 5

NOSQL_ERRMSGS = {
    SUCCESS: "success",
    ERR_NODATABASE: "No such database",
    ERR_INVALIDCMD: "Invalid command",
    ERR_INVALIDKEY: "Invalid key",
    ERR_INVALIDVALUE: "Invalid value",
    ERR_NOKEY: "No such key",
}


