# -*- coding: utf-8 -*-
# Description @
#  CreateTime @2017-05-24 13:50:50

import os
import pickle
import zlib
import sys

class DBClient:
    def __init__(self, sockconn, passwd):
        self.isauth = False
        self.passwd = passwd
        self.sockconn = sockconn
        self.message = u""
        self.response = None

class Database:
    def __init__(self, enauth=False, passwd=None, dbfile="dump.db"):
        self.__dbid__ = 0
        self.__databases__ = {}
        self.__enauth__ = enauth
        self.__passwd__ = passwd
        self.__dbfile__ = dbfile if dbfile else "dump.db"
        self.__clients__ = {}

        if os.path.exists(self.__dbfile__):
            if os.path.getsize(self.__dbfile__):
                dbs = None
                with open(self.__dbfile__, "rb") as f:
                    dbs = pickle.load(f)

                # verify cksum
                cksum = zlib.crc32(pickle.dumps(dbs["db"]))
                if cksum != dbs["cksum"]:
                    print("Database is modified by user!!!!")
                    sys.exit(1)

                self.__databases__ = dbs["db"]

    def save(self):
        if self.__databases__:
            try:
                dbs = {
                        "db": self.__databases__,
                }
                cksum = zlib.crc32(pickle.dumps(self.__databases__))
                dbs["cksum"] = cksum
                with open(self.__dbfile__, "wb") as f:
                    pickle.dump(dbs, f)
            except Exception as e:
                return False

        return True

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

    def get_databases(self):
        return self.__databases__

    def get_enauth(self):
        return self.__enauth__

    def get_passwd(self):
        return self.__passwd__

    def add_client(self, sockconn, authpwd=None):
        if sockconn.fileno() in self.__clients__:
            return True

        client = DBClient(sockconn, authpwd)
        self.__clients__[sockconn.fileno()] = client

        return True

    def delete_client(self, sockfd):
        if sockfd not in self.__clients__:
            return False

        self.__clients__[sockfd].sockconn.close()
        del self.__clients__[sockfd]

    def get_client(self, sockfd):
        if sockfd not in self.__clients__:
            return None

        return self.__clients__[sockfd]


