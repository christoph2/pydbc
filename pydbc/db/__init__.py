#!/usr/bin/env python
# -*- coding: utf-8 -*-

__copyright__ = """
   pySART - Simplified AUTOSAR-Toolkit for Python.

   (C) 2010-2018 by Christoph Schueler <cpu12.gems.googlemail.com>

   All Rights Reserved

   This program is free software; you can redistribute it and/or modify
   it under the terms of the GNU General Public License as published by
   the Free Software Foundation; either version 2 of the License, or
   (at your option) any later version.

   This program is distributed in the hope that it will be useful,
   but WITHOUT ANY WARRANTY; without even the implied warranty of
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
   GNU General Public License for more details.

   You should have received a copy of the GNU General Public License along
   with this program; if not, write to the Free Software Foundation, Inc.,
   51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

   s. FLOSS-EXCEPTION.txt
"""
__author__  = 'Christoph Schueler'
__version__ = '0.1.0'

from collections import namedtuple
import itertools
import logging
import mmap
from pprint import pprint
import re
import sqlite3
import types

from pydbc.exceptions import DuplicateKeyError
from pydbc.logger import Logger


PAGE_SIZE = mmap.PAGESIZE

def regexer(expr, value):
    return re.search(expr, value, re.UNICODE) is not None

def calculateCacheSize(value):
    return -(value // PAGE_SIZE)

class CanDatabase(object):

    def __init__(self, filename = ":memory:", cachesize = 4, logLevel = 'INFO'):
        self.conn = sqlite3.connect(filename, isolation_level = None)
        self.conn.create_function("REGEXP", 2, regexer)
        self.conn.isolation_level = None
        self.cachesize = cachesize
        self.setPragmas()
        self.filename = filename
        self.logger = Logger('db', level = logLevel)

    def __del__(self):
        self.conn.close()

    def close(self):
        self.conn.close()

    def getCursor(self):
        return self.conn.cursor()

    def setPragma(self, cur, key, value):
        cur.execute("PRAGMA {} = {}".format(key, value))

    def setPragmas(self):
        cur = self.getCursor()
        self.setPragma(cur, "FOREIGN_KEYS", "ON")
        self.setPragma(cur, "PAGE_SIZE", "{}".format(PAGE_SIZE))
        self.setPragma(cur, "CACHE_SIZE", "{}".format(calculateCacheSize(self.cachesize * 1024 * 1024)))
        self.setPragma(cur, "SYNCHRONOUS", "OFF")   # FULL
        self.setPragma(cur, "LOCKING_MODE", "EXCLUSIVE")    # NORMAL
        self.setPragma(cur, "TEMP_STORE", "MEMORY") # FILE
        """

        #self.cur.execute('PRAGMA journal_mode = MEMORY')   # TRUNCATE
        #self.cur.execute('PRAGMA journal_mode = WAL')
        """

    def beginTransaction(self):
        self.conn.execute("BEGIN TRANSACTION")

    def commitTransaction(self):
        self.conn.commit()

    def rollbackTransaction(self):
        self.conn.rollback()

    #def lastInsertedRowId(self, cur, table):
    #    rowid = cur.lastrowid
    #    return rowid

    def createDictFromRow(self, row, description):
        names = [d[0] for d in description]
        di = dict(zip(names, row))
        return di

    def fetchSingleRow(self, cur, tname, column, where):
        cur.execute("""SELECT {} FROM {} WHERE {}""".format(column, tname, where))
        row = cur.fetchone()
        if row is None:
            return []
        return self.createDictFromRow(row, cur.description)

    def fetchSingleValue(self, cur, tname, column, where):
        cur.execute("""SELECT {} FROM {} WHERE {}""".format(column, tname, where))
        result = cur.fetchone()
        if result is None:
            return []
        return result[0]

    def queryStatement(self, tname, columns = None, where = None, orderBy = None):
        pass

    def updateStatement(self, cur, tname, columns, where, *values):
        columns = [c.strip() for c in columns.split(",")]
        colStmt = ', '.join(["{} = ?".format(c) for c in columns])
        sql = "UPDATE OR FAIL {} SET {} WHERE {}".format(tname, colStmt, where)
        try:
            res = cur.execute(sql, *values)
        except sqlite3.DatabaseError as e:
            excText = str(e)
            msg = "{} - Table: '{}'; Data: {}".format(excText, tname, values)
            self.logger.debug(msg)
            if excText.startswith("UNIQUE constraint failed:"):
                ii = excText.find(":")
                raise DuplicateKeyError("Table: '{}'; Key-Column: '{}'; Data: {}".format(tname, excText[ii + 2 : ], values)) from None
            else:
                raise

    def insertOrReplaceStatement(self, insert, cur, tname, columns, *values):
        """
        """
        verb = "INSERT OR FAIL" if insert else "REPLACE"
        try:
            placeholder = ','.join("?" * len(values))
            stmt = "{} INTO {}({}) VALUES({})".format(verb, tname, columns, placeholder)
            cur.execute(stmt, [*values])
        except sqlite3.DatabaseError as e:
            msg = "{} - Data: {}".format(str(e), values)
            self.logger.error(msg)
            return None
        else:
            return cur.lastrowid

    def insertStatement(self, cur, tname, columns, *values):
        return self.insertOrReplaceStatement(True, cur, tname, columns, *values)

    def replaceStatement(self, cur, tname, columns, *values):
        return self.insertOrReplaceStatement(False, cur, tname, columns, *values)

    def fetchFromTable(self, cur, tname, columns = None, where = None, orderBy = None):
        whereClause = "" if not where else "WHERE {}".format(where)
        orderByClause = "ORDER BY rowid" if not orderBy else "ORDER BY {}".format(orderBy)
        result = cur.execute("""SELECT * FROM {} {} {}""".format(tname, whereClause, orderByClause), [])
        while True:
            row = cur.fetchone()
            if row is None:
                return
            else:
                yield self.createDictFromRow(row, cur.description)

