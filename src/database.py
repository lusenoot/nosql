# -*- coding: utf-8 -*-
# Description @
#  CreateTime @2017-05-24 13:50:50

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

    def get_enauth(self):
        return self.__enauth__

    def get_passwd(self):
        return self.__passwd__


