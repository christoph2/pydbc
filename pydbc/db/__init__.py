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

#import pkg_resources
#pkg_resources.declare_namespace(__name__)

from collections import namedtuple
import itertools
import logging
from pprint import pprint
import sqlite3
import types

from pydbc.logger import Logger


from profilehooks import profile

logging.basicConfig()

#@profile(immediate = True)
class CanDatabase(object):

    def __init__(self, filename = ":memory:"):
        self.conn = sqlite3.connect(filename, isolation_level = None)
        self.conn.isolation_level = None
        self.filename = filename
        self.logger = Logger('db')

    def __del__(self):
        self.conn.close()

    def getCursor(self):
        return self.conn.cursor()

    def beginTransaction(self):
        self.conn.execute("BEGIN TRANSACTION")

    def commitTransaction(self):
        self.conn.commit()

    def rollbackTransaction(self):
        self.conn.rollback()

    def lastInsertedRowId(self, cur, table):
        rowid = cur.lastrowid
        result = cur.execute("SELECT RID FROM {} WHERE rowid = ?".format(table), [rowid]).fetchone()
        return result[0]

    def fetchComment(self, tp, k0, k1 = None):
        cur = self.getCursor()
        if k1:
            cur.execute("SELECT comment FROM comments WHERE type = ? AND k0 = ? AND k1 = ?;", [tp, k0, k1])
        else:
            cur.execute("SELECT comment FROM comments WHERE type = ? AND k0 = ?;", [tp, k0])
        cmt = cur.fetchall()
        if cmt:
            assert len(cmt[0]) <= 1
            return cmt[0][0]
        else:
            return None

    def fetchEnvironmentVariablesData(self, name):
        cur = self.getCursor()
        cur.execute("SELECT value FROM EnvironmentVariablesData WHERE name = ?", [name])
        value = cur.fetchall()
        if value:
            return value[0][0]
        return None

    def fetchNodeId(self, name):
        cur = self.getCursor()
        cur.execute("""SELECT RID FROM Node WHERE Name = ?""", [name])
        result = cur.fetchone()[0]
        return result

    def fetchMessageIdById(self, messageId):
        cur = self.getCursor()
        cur.execute("""SELECT RID FROM Message WHERE Message_ID = ?""", [messageId])
        result = cur.fetchone()[0]
        return result

    def fetchEnvVarId(self, name):
        cur = self.getCursor()
        cur.execute("""SELECT RID FROM EnvVar WHERE Name = ?""", [name])
        result = cur.fetchone()[0]
        return result

    def fetchAttributeId(self, name):
        cur = self.getCursor()
        cur.execute("""SELECT RID FROM Attribute_Definition WHERE Name = ?""", [name])
        result = cur.fetchone()[0]
        return result

    def fetchMessageIdByName(self, name):
        cur = self.getCursor()
        cur.execute("""SELECT RID FROM Message WHERE Name = ?""", [name])
        result = cur.fetchone()[0]
        return result

    def fetchSignalReceivers(self, messageId, signalId):
        cur = self.getCursor()
        cur.execute("SELECT (SELECT name FROM Node WHERE RID=node) FROM Node_RxSignal WHERE message=? and signal=?", [messageId, signalId])
        result = [x[0] for x in cur.fetchall()]
        return result

    def spaceBeforeNodes(self, nodes):
        if len(nodes) == 1 and nodes[0] == 'Vector__XXX':
            return ''
        else:
            return ' '

    def createDictFromRow(self, row, description):
        names = [d[0] for d in description]
        di = dict(zip(names, row))
        return di

    @property
    def nodeNames(self):
        cur = self.getCursor()
        res = cur.execute("""SELECT Name FROM Node WHERE RID > 0""", []).fetchall()
        res = [x[0] for x in res]
        return res

    def nodeName(self, nid):
        cur = self.getCursor()
        res = cur.execute("""SELECT Name FROM Node WHERE RID = ?""", [nid]).fetchall()
        return res[0][0]

    def signals(self, messageId):
        cur = self.getCursor()
        res = cur.execute("""SELECT * FROM message_signal AS t1, signal AS t2 WHERE t1.message = ? AND t1.signal = t2.RID""", [messageId])
        while True:
            row = cur.fetchone()
            if row is None:
                raise StopIteration
            else:
                yield self.createDictFromRow(row, cur.description)

    def fetchSingleValue(self, tname, column, where):
        cur = self.getCursor()
        cur.execute("""SELECT {} FROM {} WHERE {} = ?""".format(column, tname), [where])
        result = cur.fetchone()[0]
        return result

    def queryStatement(self, tname, columns = None, where = None, orderBy = None):
        pass

    def insertOrReplaceStatement(self, insert, cur, tname, columns, *values):
        verb = "INSERT OR FAIL" if insert else "REPLACE"
        try:
            placeholder = ','.join("?" * len(values))
            stmt = "{} INTO {}({}) VALUES({})".format(verb, tname, columns, placeholder)
            cur.execute(stmt, [*values])
        except sqlite3.DatabaseError as e:
            msg = "{} - Data: {}".format(str(e), values)
            self.logger.error(msg)
            return False
        else:
            return True

    def insertStatement(self, cur, tname, columns, *values):
        return self.insertOrReplaceStatement(True, cur, tname, columns, *values)

    def replaceStatement(self, cur, tname, columns, *values):
        return self.insertOrReplaceStatement(False, cur, tname, columns, *values)
        #try:
        #    placeholder = ','.join("?" * len(values))
        #    stmt = "INSERT OR FAIL INTO {}({}) VALUES({})".format(tname, columns, placeholder)
        #    cur.execute(stmt, [*values])
        #except sqlite3.DatabaseError as e:
        #    msg = "{} - Data: {}".format(str(e), values)
        #    self.logger.error(msg)
        #    return False
        #else:
        #    return True

    def fetchSignalValue(self):
        pass

    def fetchSignalValues(self):
        pass

    def fetchFromTable(self, tname, columns = None, where = None, orderBy = None):
        cur = self.getCursor()
        whereClause = "" if not where else "WHERE {}".format(where)
        orderByClause = "ORDER BY rowid" if not orderBy else "ORDER BY {}".format(orderBy)
        result = cur.execute("""SELECT * FROM {} {} {}""".format(tname, whereClause, orderByClause), [])
        while True:
            row = cur.fetchone()
            if row is None:
                raise StopIteration
            else:
                yield self.createDictFromRow(row, cur.description)

    def multiplexIndicator(self, value):
        if value['Multiplexor_Signal']:
            return 'M '
        elif value['Multiplex_Dependent']:
            return "m{} ".format(value['Multiplexor_Value'])
        else:
            return ''

    def messages(self):
        yield from self.fetchFromTable("Message")

    def comments(self):
        yield from self.fetchFromTable("comments")

    def valueTablesGlobal(self):
        yield from self.fetchFromTable("Valuetable", where = "RID NOT IN (SELECT valuetable FROM Object_Valuetable)")

    def attributeDefinitions(self):
        yield from self.fetchFromTable("Attribute_Definition")

    def environmentVariables(self):
        yield from self.fetchFromTable("EnvVar")

    def messageIdFromRid(self, rid):
        cur = self.getCursor()
        cur.execute("""SELECT t2.message_id FROM message_signal AS t1, Message AS t2 WHERE t1.signal = ? AND t1.message = t2.RID""", [rid])
        res = cur.fetchone()[0]
        #print("messageIdFromRid", res)
        return res

    def valueTablesLocal(self):
        cur = self.getCursor()
        res = cur.execute("""SELECT * FROM Object_Valuetable AS t1, Valuetable AS t2 WHERE t1.valuetable=t2.RID""", [])
        while True:
            row = cur.fetchone()
            if row is None:
                raise StopIteration
            else:
                vt = self.createDictFromRow(row, cur.description)
                if vt['Object_Type'] == 0:
                    messageId = self.messageIdFromRid(vt['Object_RID'])
                    vt['Message_ID'] = messageId
                yield vt

    def envVarAccessNodes(self, envVarId):
        cur = self.getCursor()
        res = cur.execute("""SELECT name FROM EnvVar_AccessNode AS t1, Node AS t2 WHERE t1.node=t2.RID AND EnvVar=?""", [envVarId])
        while True:
            row = cur.fetchone()
            if row is None:
                raise StopIteration
            else:
                yield row[0]

    def valueDescription(self, tableId, srt = True):
        orderBy = "value desc" if srt else None
        yield from self.fetchFromTable("Value_Description", where = "Valuetable = {}".format(tableId), orderBy = orderBy)

    def multipleTransmitters(self):
        cur = self.getCursor()
        cur.execute("""SELECT message, message_id, COUNT(Node) AS nc FROM Node_TxMessage AS t1,
            Message AS t2 WHERE t1.message = t2.rid GROUP BY message HAVING nc > 1;"""
        )
        rows = cur.fetchall()
        if rows:
            messages = {r[0]:r[1] for r in rows}
            stmt = """SELECT node, message, name FROM Node_TxMessage AS t1, Node AS t2 WHERE t1.Node = t2.rid
                AND message IN {};
            """.format(tuple(messages.keys()))
            cur.execute(stmt)
            items = cur.fetchall()
            for kr, item in itertools.groupby(items, lambda n: n[1]):
                senders = []
                for (nrid, mrid, name) in item:
                    senders.append(name)
                yield((messages[kr], (senders)))
        else:
            return []