# -*- coding: utf-8 -*-

from constants import *
from database import Database

import pickle

databases = None
def init_database(enauth=False, passwd=None):
    global databases
    if not databases:
        databases = Database(enauth, passwd)

def add_client(sockconn, authpwd=None):
    if not databases:
        return False

    databases.add_client(sockconn, authpwd)
    return True

def delete_client(sockfd):
    databases.delete_client(sockfd)

def get_client(sockfd):
    return databases.get_client(sockfd)

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

def check_auth(func):
    def wrapper(*args, **kwargs):
        client = args[0]

        if not client:
            return False, ERR_INVALIDPARAM, None

        if not client.isauth:
            if databases.get_enauth() and databases.get_passwd():
                # check client auth passwd
                if not client.passwd or client.passwd != databases.get_passwd():
                    return False, ERR_AUTHFAILED, None
                client.isauth = True
            else:
                client.isauth = True

        return func(*args, **kwargs)

    return wrapper

@check_auth
def handle_set(client, key, value, valuetype=VT_STRING, dbid=-1):
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

@check_auth
def handle_get(client, key, dbid=-1):
    if key is None:
        return False, ERR_INVALIDKEY, None

    db = databases.get_database(dbid)
    if not db:
        return False, ERR_NODATABASE, None

    if key not in db:
        return False, ERR_NOKEY, None

    return True, SUCCESS, db[key]

@check_auth
def handle_lpush(client, key, value, valuetype=VT_LIST, dbid=-1):
    return handle_set(client, key, value, valuetype, dbid)

@check_auth
def handle_lpop(client, key, dbid=-1):
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

@check_auth
def handle_delete(client, key, dbid=-1):
    flag, code, value = handle_get(client, key, dbid)
    if not flag:
        return flag, code, None

    db = databases.get_database(dbid)

    return True, SUCCESS, db.pop(key)

@check_auth
def handle_select(client, dbid=-1):
    flag = databases.setdbid(dbid)
    if not flag:
        return False, ERR_NODATABASE, None

    return True, SUCCESS, None

@check_auth
def handle_keys(client, dbid=-1):
    db = databases.get_database(dbid)
    if not db:
        return False, ERR_NODATABASE, None

    keys = []
    for key in db:
        keys.append(key)

    return True, SUCCESS, keys

def handle_auth(client, passwd):
    if not databases.get_enauth():
        return True, SUCCESS, None

    if not passwd or passwd != databases.get_passwd():
        return False, ERR_AUTHFAILED, None

    client.isauth = True
    client.passwd = passwd

    databases.update_client(client)

    return True, SUCCESS, None

@check_auth
def handle_save(client):
    try:
        if not databases.save():
            return False, ERR_SAVEFAILED, None
    except Exception as e:
        print(e)
        return False, ERR_SAVEFAILED, None

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
    COMMAND_SAVE: {"func": handle_save, "needparam": 0, "isquery": 0},
}


