# -*- coding: utf-8 -*-

from constants import *

class Database:
    def __init__(self, enauth=False, passwd=None):
        self.__dbid__ = 0
        self.__databases__ = {}
        self.__enauth__ = enauth
        self.__passwd__ = passwd

    def getdbid(self):
        return self.___dbid__

    def setdbid(self, dbid):
        if dbid in self.__databases__:
            self.__dbid__ = dbid
            return True

        return False

    def get_database(self, dbid, addnew=False):
        if dbid == -1:
            dbid = self.__dbid__

        if dbid not in self.__databases__:
            if addnew:
                self.__databases__[dbid] = {}
            else:
                return None

        return self.__databases__[dbid]

databases = None

def init_database(enauth=False, passwd=None):
    global databases
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
        return False, ERR_INVALIDVALUE, None

    if valuetype == VT_NUMBER or valuetype == VT_STRING:
        db[key] = value
    elif valuetype == VT_LIST:
        try:
            values = map(lambda val: val.strip(), value.strip().split(","))
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

NOSQL_COMMANDS = {
    COMMAND_SET: {"func": handle_set, "needparam": 2, "isquery": 0},
    COMMAND_GET: {"func": handle_get, "needparam": 1, "isquery": 1},
    COMMAND_LPUSH: {"func": handle_lpush, "needparam": 2, "isquery": 0},
    COMMAND_LPOP: {"func": handle_lpop, "needparam": 2, "isquery": 0},
    COMMAND_DELETE: {"func": handle_delete, "needparam": 1, "isquery": 0},
    COMMAND_SELECT: {"func": handle_select, "needparam": 1, "isquery": 1},
    COMMAND_KEYS: {"func": handle_keys, "needparam": 0, "isquery": 1},
    #COMMAND_AUTH: {"func": handle_auth, "needparam": 1, "isquery": 0},
}


