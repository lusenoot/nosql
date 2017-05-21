# -*- coding: utf-8 -*-

from constants import *

curr_dbid = 0
databases = {}

def __validate_vt(valuetype):
    if not valuetype:
        return None

    if valuetype == VT_NUMBER:
        return VT_NUMBER
    elif valuetype == VT_STRING:
        return VT_STRING

    return None

def handle_put(key, value, valuetype="string", dbid=-1):
    if key is None:
        return False, ERR_INVALIDKEY, None

    if dbid == -1:
        dbid = curr_dbid

    if dbid not in databases:
        databases[dbid] = {}

    if not __validate_vt(valuetype):
        return False, ERR_INVALIDVALUE, None

    if valuetype == VT_NUMBER or valuetype == VT_STRING:
        databases[dbid][key] = value

    return True, SUCCESS, value

def handle_get(key, dbid=-1):
    if key is None:
        return False, ERR_INVALIDKEY, None

    if dbid == -1:
        dbid = curr_dbid

    if dbid not in databases:
        return False, ERR_NODATABASE, None

    if key not in databases[dbid]:
        return False, ERR_NOKEY, None

    return True, SUCCESS, databases[dbid][key]

def handle_delete(key, dbid=-1):
    flag, code, value = handle_get(key, dbid)
    if not flag:
        return flag, code, None

    if dbid == -1:
        dbid = curr_dbid

    return True, SUCCESS, databases[dbid].pop(key)

def handle_select(dbid=-1):
    if dbid == -1:
        dbid = curr_dbid

    if dbid not in databases:
        return False, ERR_NODATABASE, None

    curr_dbid = dbid

    return True, SUCCESS, None

def handle_keys(dbid=-1):
    if dbid == -1:
        dbid = curr_dbid

    if dbid not in databases:
        return False, ERR_NODATABASE, None

    keys = []
    for key in databases[dbid]:
        keys.append(key)

    return True, SUCCESS, keys

NOSQL_COMMANDS = { 
    COMMAND_PUT: {"func": handle_put, "needparam": 2, "isquery": 0}, 
    COMMAND_GET: {"func": handle_get, "needparam": 1, "isquery": 1}, 
    COMMAND_DELETE: {"func": handle_delete, "needparam": 1, "isquery": 0}, 
    COMMAND_SELECT: {"func": handle_select, "needparam": 1, "isquery": 1}, 
    COMMAND_KEYS: {"func": handle_keys, "needparam": 0, "isquery": 1}, 
}


