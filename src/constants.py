# -*- coding: utf-8 -*-

COMMAND_SET = "set"
COMMAND_LPUSH = "lpush"
COMMAND_LPOP = "lpop"
COMMAND_GET = "get"
COMMAND_DELETE = "delete"
COMMAND_SELECT = "select"
COMMAND_KEYS = "keys"
COMMAND_AUTH = "auth"

VT_NUMBER = "number"
VT_STRING = "string"
VT_LIST = "list"

SUCCESS = 0
ERR_NODATABASE = 1
ERR_INVALIDCMD = 2
ERR_INVALIDKEY = 3
ERR_INVALIDVALUE = 4
ERR_INVALIDVALUETYPE = 5
ERR_NOKEY = 6
ERR_AUTHFAILED = 9

NOSQL_ERRMSGS = {
    SUCCESS: "success",
    ERR_NODATABASE: "No such database",
    ERR_INVALIDCMD: "Invalid command",
    ERR_INVALIDKEY: "Invalid key",
    ERR_INVALIDVALUE: "Invalid value",
    ERR_INVALIDVALUETYPE: "Invalid value type",
    ERR_NOKEY: "No such key",
    ERR_AUTHFAILED: "Auth failed",
}


