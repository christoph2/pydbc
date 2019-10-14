#!/usr/bin/env python
# -*- coding: utf-8 -*-

__copyright__ = """
   pySART - Simplified AUTOSAR-Toolkit for Python.

   (C) 2010-2019 by Christoph Schueler <cpu12.gems.googlemail.com>

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

from pydbc.logger import Logger
from pydbc.types import AttributeType, ValueType, CategoryType

class Queries:
    """
    """

    def __init__(self, db):
        self.logger = Logger(__name__)
        self.db = db

    def getCursor(self):
        return self.db.getCursor()

    def fetchEnvironmentVariablesData(self, name):
        cur = self.getCursor()
        return self.db.fetchSingleValue(cur, "EnvironmentVariablesData", "value", "name = '{}'".format(name))

    def environmentVariablesData(self):
        cur = self.getCursor()
        yield from self.db.fetchFromTable(cur, "EnvironmentVariablesData", "*")

    def fetchNodeId(self, name):
        cur = self.getCursor()
        return self.db.fetchSingleValue(cur, "Node", "RID", "Name = '{}'".format(name))

    def fetchNodenameByRid(self, rid):
        cur = self.getCursor()
        return self.db.fetchSingleValue(cur, "Node", "Name", "RID = {}".format(rid))

    def fetchEnvvarNameByRid(self, rid):
        cur = self.getCursor()
        return self.db.fetchSingleValue(cur, "EnvVar", "Name", "RID = {}".format(rid))

    def fetchMessageIdByRid(self, rid):
        cur = self.getCursor()
        return self.db.fetchSingleValue(cur, "Message", "Message_ID", "RID = {}".format(rid))

    def fetchMessageIdById(self, messageId):
        cur = self.getCursor()
        return self.db.fetchSingleValue(cur, "Message", "RID", "Message_ID = {}".format(messageId))

    def fetchEnvVarId(self, name):
        cur = self.getCursor()
        return self.db.fetchSingleValue(cur, "EnvVar", "RID", "Name = '{}'".format(name))

    def fetchAttributeId(self, name):
        cur = self.getCursor()
        return self.db.fetchSingleValue(cur, "Attribute_Definition", "RID", "Name = '{}'".format(name))

    def fetchMessageIdByName(self, name):
        cur = self.getCursor()
        return self.db.fetchSingleValue(cur, "Message", "RID", "Name = '{}'".format(name))

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

    def fetchMessageSignalByMessageIDandSignalName(self, messageID, signalName):
        cur = self.getCursor()
        cur.execute("""SELECT  t2.Message, t2.Signal FROM Message AS t1, Message_Signal AS t2, Signal AS t3 WHERE
            t1.Message_Id = {} AND t2.Message = t1.RID AND t2.Signal = t3.RID AND t3.Name = '{}'
        """.format(messageID, signalName))
        result = cur.fetchone()
        return result

    def fetchSignalGroups(self):
        cur = self.getCursor()
        cur.execute("""SELECT t1.RID, t1.Name, t1.Value,
            (SELECT t2.Message_Id FROM Message AS t2 WHERE t2.RID = t1.Message) AS Message_Id FROM Signal_Group as t1
            ORDER BY t1.RID
        """)
        while True:
            row = cur.fetchone()
            if row is None:
                return
            else:
                result = self.db.createDictFromRow(row, cur.description)
                cur2 = self.getCursor()
                rid = row[0]
                res2 = cur2.execute("""SELECT (SELECT t2.Name FROM Signal AS t2 WHERE t2.RID = t1.signal) AS Name
                FROM Signal_Group_Signal AS t1 WHERE t1.Signal_Group = {}""".format(rid))
                signals = [s[0] for s in cur2.fetchall()]
                result.update(Signals = signals)
                yield result

    def fetchSignalReceivers(self, messageId, signalId):
        cur = self.getCursor()
        cur.execute("SELECT (SELECT name FROM Node WHERE RID = node) FROM Node_RxSignal WHERE message=? and signal=?", [messageId, signalId])
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

    def relativeAttributeValues(self):
        cur = self.getCursor()
        yield from self.db.fetchFromTable(cur, "AttributeRel_Value")

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
            key ="({})".format(','.join([str(k) for k in messages.keys()]))
            stmt = """SELECT node, message, name FROM Node_TxMessage AS t1, Node AS t2 WHERE t1.Node = t2.rid
                AND message IN {};
            """.format(key)
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


class LinQueries(Queries):
    """
    """

    def getAttributeDefinitionByName(self, name):
        """
        """
        cur = self.getCursor()
        result = list(self.db.fetchFromTable(cur, "linAttribute_Definition", where = "name = '{}'".format(name)))
        if result:
            return result[0]
        else:
            return {}

    def getAttributeValues(self, name):
        cur = self.getCursor()
        attrDef = self.getAttributeDefinitionByName(name)
        if attrDef:
            rid = attrDef.get("RID")
            return list(self.db.fetchFromTable(cur, "linAttribute_Value", where = "Attribute_Definition = {}".format(rid)))
        else:
            return []

    def masterNode(self):
        """Get basic information about master node.

        Returns
        -------
            tuple
                - node_name: str
                - timebase: int
                - jitter: int
        """
        cur = self.getCursor()
        result = self.getAttributeValues("LIN_is_master")

        if len(result) == 0:
            self.logger.warn("No master node specified.")
        elif len(result) > 1:
            self.logger.warn("Multiple master nodes specified.")
        else:
            rid = result[0].get("Object_ID")
            node = list(self.db.fetchFromTable(cur, "Node", where = "RID = {}".format(rid)))
            name = node[0].get("Name")
            tb = int(list(self.getAttributeValues("LIN_time_base"))[0].get("Num_Value"))
            jt = int(list(self.getAttributeValues("LIN_jitter"))[0].get("Num_Value"))
            return name, tb, jt

    def slaveNodeNames(self):
        """Get slave node names.

        Returns
        -------
            list - Names of slave nodes.
        """
        cur = self.getCursor()
        slaveIDs = [s['Object_ID'] for s in self.getAttributeValues("LIN_is_slave")]
        cur.execute("SELECT Name from Node WHERE RID in ({}) ORDER BY RID".format(','.join([str(s) for s in slaveIDs])))
        slaves =  [s[0] for s in cur.fetchall()]
        return slaves

    def frames(self):
        """
        """
        cur = self.getCursor()
        frames = list(self.db.fetchFromTable(cur, "Message", columns = "RID, Name, Message_ID, DLC, Sender", orderBy = "RID"))
        for frame in frames:
            mrid = frame['RID']
            sender = self.fetchNodenameByRid(frame['Sender'])
            frame.update(Sender = sender)
            cur.execute("SELECT Signal, Offset FROM Message_Signal WHERE Message = {} ORDER BY 1".format(mrid))
            rows = cur.fetchall()
            messageSignals = []
            for row in rows:
                srid, offs = row
                messageSignals.append((self.fetchSignalNameByRid(srid), offs))
            frame.update(messageSignals = messageSignals)
        return frames

    def signals(self):
        """
        """
        cur = self.getCursor()
        signals = list(self.db.fetchFromTable(cur, "Signal", columns = "RID, Name, Bitsize", orderBy = "RID"))
        iv = list(self.getAttributeValues("LIN_signal_initial_value"))
        initialValues = dict([(x.get("Object_ID"), x.get("Num_Value")) for x in iv])
        result = []
        for signal in signals:
            name = signal.get("Name")
            rid = signal.get("RID")
            bitsize = signal.get("Bitsize")
            initialValue = initialValues[rid]
            if isinstance(initialValue, str):
                initialValue = [int(v) for v in initialValue.split(";")]
            else:
                initialValue = int(initialValue)
            nrid = self.db.fetchSingleValue(cur, "Node_TxSig", "Node", "Signal = '{}'".format(rid))
            cur.execute("SELECT name FROM node WHERE rid IN (SELECT node FROM Node_RxSignal WHERE signal = {})".format(rid))
            subscribers = [s[0] for s in cur.fetchall()]
            publisher = self.db.fetchSingleValue(cur, "Node", "Name", "RID = {}".format(nrid))
            result.append((name, bitsize, initialValue, publisher, subscribers))
        return result

    def fetchSignalNameByRid(self, rid):
        cur = self.getCursor()
        return self.db.fetchSingleValue(cur, "Signal", "Name", "RID = {}".format(rid))


    def networkAttributes(self):
        """
        """
        cur = self.getCursor()
        attrDefs = list(self.db.fetchFromTable(cur, "linAttribute_Definition", columns = "RID, Name, Valuetype",
            orderBy = "RID", where = "Objecttype = {}".format(AttributeType.NETWORK)))
        result = {}
        for attrDef in attrDefs:
            rid = attrDef.get("RID")
            name = attrDef.get("Name")
            value_type = attrDef.get("Valuetype")
            cur.execute("SELECT Num_Value, String_Value FROM linAttribute_Value WHERE Attribute_Definition = {}".format(rid))
            rvalue = cur.fetchone()
            if rvalue:
                num_value, string_value = rvalue
                if num_value is None and string_value is None:
                    continue
                value = num_value if value_type in (ValueType.INT, ValueType.FLOAT) else string_value
                result[name] = value
        return result
