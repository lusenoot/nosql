# -*- coding: utf-8 -*-

from constants import *
from database import Database

databases = None
def init_database(enauth=False, passwd=None):
    global databases
    if not databases:
        databases = Database(enauth, passwd)

def __validate_vt(valuetype):
    if not valuetype:
        return None

    if valuetype == VT_NUMBER:
        return VT_NUMBER
    elif valuetype == VT_STRING:
        return VT_STRING
    elif valuetype == VT_LIST:
        return VT_LIST

    return None

def handle_set(key, value, valuetype=VT_STRING, dbid=-1):
    if key is None:
        return False, ERR_INVALIDKEY, None

    db = databases.get_database(dbid, True)

    if not __validate_vt(valuetype):
        return False, ERR_INVALIDVALUETYPE, None

    if valuetype == VT_NUMBER or valuetype == VT_STRING:
        db[key] = value
    elif valuetype == VT_LIST:
        try:
            values = list(map(lambda val: val.strip(), value.strip().split(",")))
        except ValueError:
            return False, ERR_INVALIDVALUE, None

        if key not in db:
            db[key] = values
        else:
            if not isinstance(db[key], list):
                return False, ERR_INVALIDVALUETYPE, None

            for val in values:
                db[key].append(val)

    return True, SUCCESS, db[key]

def handle_get(key, dbid=-1):
    if key is None:
        return False, ERR_INVALIDKEY, None

    db = databases.get_database(dbid)
    if not db:
        return False, ERR_NODATABASE, None

    if key not in db:
        return False, ERR_NOKEY, None

    return True, SUCCESS, db[key]

def handle_lpush(key, value, valuetype=VT_LIST, dbid=-1):
    return handle_set(key, value, valuetype, dbid)

def handle_lpop(key, dbid=-1):
    if key is None:
        return False, ERR_INVALIDKEY, None

    db = databases.get_database(dbid)
    if not db:
        return False, ERR_NODATABASE, None

    if key not in db:
        return False, ERR_NOKEY, None

    values = db[key]
    if not isinstance(values, list):
        return False, ERR_INVALIDVALUETYPE, None

    value = values.pop(0) if len(values) > 0 else None

    return True, SUCCESS, value

def handle_delete(key, dbid=-1):
    flag, code, value = handle_get(key, dbid)
    if not flag:
        return flag, code, None

    db = databases.get_database(dbid)

    return True, SUCCESS, db.pop(key)

def handle_select(dbid=-1):
    flag = databases.setdbid(dbid)
    if not flag:
        return False, ERR_NODATABASE, None

    return True, SUCCESS, None

def handle_keys(dbid=-1):
    db = databases.get_database(dbid)
    if not db:
        return False, ERR_NODATABASE, None

    keys = []
    for key in db:
        keys.append(key)

    return True, SUCCESS, keys

def handle_auth(passwd):
    if not databases.get_enauth():
        return True, SUCCESS, None

    if not passwd or passwd != databases.get_passwd():
        return False, ERR_AUTHFAILED, None

    return True, SUCCESS, None

NOSQL_COMMANDS = {
    COMMAND_SET: {"func": handle_set, "needparam": 2, "isquery": 0},
    COMMAND_GET: {"func": handle_get, "needparam": 1, "isquery": 1},
    COMMAND_LPUSH: {"func": handle_lpush, "needparam": 2, "isquery": 0},
    COMMAND_LPOP: {"func": handle_lpop, "needparam": 2, "isquery": 0},
    COMMAND_DELETE: {"func": handle_delete, "needparam": 1, "isquery": 0},
    COMMAND_SELECT: {"func": handle_select, "needparam": 1, "isquery": 1},
    COMMAND_KEYS: {"func": handle_keys, "needparam": 0, "isquery": 1},
    COMMAND_AUTH: {"func": handle_auth, "needparam": 1, "isquery": 0},
}


