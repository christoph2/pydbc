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

import itertools

class Queries:
    """
    """

    def __init__(self, db):
        self.db = db

    def getCursor(self):
        return self.db.getCursor()

    def fetchEnvironmentVariablesData(self, name):
        cur = self.getCursor()
        cur.execute("SELECT value FROM EnvironmentVariablesData WHERE name = ?", [name])
        value = cur.fetchall()
        if value:
            return value[0][0]
        return None

    def environmentVariablesData(self):
        cur = self.getCursor()
        yield from self.db.fetchFromTable(cur, "EnvironmentVariablesData", "*")

    def fetchNodeId(self, name):
        cur = self.getCursor()
        cur.execute("""SELECT RID FROM Node WHERE Name = ?""", [name])
        result = cur.fetchone()[0]
        return result

    def fetchNodenameByRid(self, rid):
        cur = self.getCursor()
        cur.execute("""SELECT Name FROM Node WHERE RID = ?""", [rid])
        result = cur.fetchone()[0]
        return result

    def fetchEnvvarNameByRid(self, rid):
        cur = self.getCursor()
        cur.execute("""SELECT Name FROM EnvVar WHERE RID = ?""", [rid])
        result = cur.fetchone()[0]
        return result

    def fetchMessageIdByRid(self, rid):
        cur = self.getCursor()
        cur.execute("""SELECT Message_ID FROM Message WHERE RID = ?""", [rid])
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

    def fetchSignalByRid(self, rid):
        cur = self.getCursor()
        cur.execute("""SELECT * FROM Signal WHERE RID = ?""", [rid])
        result = cur.fetchone()
        return self.db.createDictFromRow(result, cur.description)

    def fetchMessageSignalByRid(self, rid):
        cur = self.getCursor()
        cur.execute("""select t2.name as Name, (select message_id from message where rid = message) as Message_ID from message_signal as t1,
            signal as t2 where t1.signal=t2.rid and signal = ?""", [rid])
        result = cur.fetchone()
        return self.db.createDictFromRow(result, cur.description)

    def fetchSignalReceivers(self, messageId, signalId):
        cur = self.getCursor()
        cur.execute("SELECT (SELECT name FROM Node WHERE RID=node) FROM Node_RxSignal WHERE message=? and signal=?", [messageId, signalId])
        result = [x[0] for x in cur.fetchall()]
        return result

    def fetchExtendedSignalValueTypes(self):
        cur = self.getCursor()
        cur.execute("""SELECT t2.name AS Name, (SELECT message_id FROM message WHERE rid = message) AS Message_ID,
                    valuetype FROM message_signal AS t1,signal AS t2 WHERE t1.signal=t2.rid and valuetype != 0"""
        )
        while True:
            row = cur.fetchone()
            if row is None:
                return
            else:
                yield self.db.createDictFromRow(row, cur.description)

    def spaceBeforeNodes(self, nodes):
        if len(nodes) == 1 and nodes[0] == 'Vector__XXX':
            return ''
        else:
            return ' '

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

    def dbcVersion(self, networkId = 0):
        cur = self.getCursor()
        res = cur.execute("""SELECT Version_String FROM Dbc_Version WHERE Network = ?""", [networkId]).fetchone()
        return res[0]

    def signals(self, messageId):
        cur = self.getCursor()
        res = cur.execute("""SELECT * FROM message_signal AS t1, signal AS t2 WHERE t1.message = ? AND t1.signal = t2.RID""", [messageId])
        while True:
            row = cur.fetchone()
            if row is None:
                return
            else:
                yield self.db.createDictFromRow(row, cur.description)

    def fetchSignalValue(self):
        pass

    def fetchSignalValues(self):
        pass

    def multiplexIndicator(self, value):
        if value['Multiplexor_Signal']:
            return 'M '
        elif value['Multiplex_Dependent']:
            return "m{} ".format(value['Multiplexor_Value'])
        else:
            return ''

    def messages(self):
        cur = self.getCursor()
        yield from self.db.fetchFromTable(cur, "Message")

    def comments(self):
        cur = self.getCursor()
        cur.execute("SELECT name, comment FROM network WHERE comment IS NOT NULL")
        result = cur.fetchone()
        if result:
            name, comment = result
            yield dict(type = "NW", k0 = name, k1 = None, comment = comment)
        cur.execute("SELECT name, comment FROM node WHERE comment IS NOT NULL AND name <> 'Vector__XXX'")
        result = cur.fetchall()
        for name, comment in result:
            yield dict(type = 'BU', k0 = name, k1 = None, comment = comment)
        cur.execute("SELECT rid, message_id, comment FROM message") #  WHERE comment IS NOT NULL
        while True:
            row = cur.fetchone()
            if row is None:
                break
            else:
                mRid, msgId, mComment = row
                if mComment:
                    yield dict(type = 'BO', k0 = msgId, k1 = None, comment = mComment)
                cur2 = self.getCursor()
                cur2.execute("""SELECT DISTINCT(name), comment FROM signal WHERE rid IN
                    (SELECT signal FROM message_signal WHERE message = ?) AND comment IS NOT NULL""", [mRid])
                result = cur2.fetchall()
                for name, sComment in result:
                    yield dict(type = 'SG', k0 = msgId, k1 = name, comment = sComment)
        cur.execute("SELECT name, comment FROM envvar WHERE comment IS NOT NULL")
        result = cur.fetchall()
        for name, comment in result:
            yield dict(type = 'EV', k0 = name, k1 = None, comment = comment)

    def valueTablesGlobal(self):
        cur = self.getCursor()
        yield from self.db.fetchFromTable(cur, "Valuetable", where = "RID NOT IN (SELECT valuetable FROM Object_Valuetable)")

    def attributeDefinitions(self):
        cur = self.getCursor()
        yield from self.db.fetchFromTable(cur,"Attribute_Definition")

    def attributeValues(self):
        cur = self.getCursor()
        yield from self.db.fetchFromTable(cur, "Attribute_Value")

    def environmentVariables(self):
        cur = self.getCursor()
        yield from self.db.fetchFromTable(cur, "EnvVar")

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
                return
            else:
                vt = self.db.createDictFromRow(row, cur.description)
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
                return
            else:
                yield row[0]

    def attributeDefintion(self, attributeId):
        cur = self.getCursor()
        yield from self.db.fetchFromTable(cur, "Attribute_Definition", where = "RID = {}".format(attributeId))

    def valueDescription(self, tableId, srt = True):
        cur = self.getCursor()
        orderBy = "value desc" if srt else None
        yield from self.db.fetchFromTable(cur, "Value_Description", where = "Valuetable = {}".format(tableId), orderBy = orderBy)

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

    def categoryDefinitions(self):
        cur = self.getCursor()
        yield from self.db.fetchFromTable(cur, "Category_Definition")

    def categoryValues(self):
        cur = self.getCursor()
        yield from self.db.fetchFromTable(cur, "Category_Value")

