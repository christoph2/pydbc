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
import enum
from pprint import pprint
import sqlite3
import types

from pydbc.db.schema import TABLES, VIEWS, SCHEMA, INDICES, TRIGGER

class AttributeType(enum.IntEnum):
    NODE = 0
    MESSAGE = 1
    SIGNAL = 2
    ENV_VAR = 3
    GENERAL = 4


class ValueType(enum.IntEnum):
    INT = 0
    HEX = 1
    FLOAT = 2
    STRING = 3
    ENUM = 4

class CanDatabase(object):

    def __init__(self, filename = ":memory:"):
        self.conn = sqlite3.connect(filename, isolation_level = None)
        self.conn.isolation_level = None
        self.filename = filename
        self.dropTables()
        self.createSchema(filename)

    def __del__(self):
        self.conn.close()

    def createIndices(self):
        cur = self.getCursor()
        cur.execute("BEGIN TRANSACTION;")
        for item in INDICES:
            #print(item)
            res = cur.execute(item)
        self.conn.commit()

    def getCursor(self):
        return self.conn.cursor()

    def dropTables(self):
        cur = self.getCursor()
        cur.execute("BEGIN TRANSACTION;")
        for item in TABLES:
            #print(item)
            res = cur.execute("DROP TABLE IF EXISTS {}".format(item))
        for item in VIEWS:
            #print(item)
            res = cur.execute("DROP VIEW IF EXISTS {}".format(item))
        self.conn.commit()

    def createSchema(self, filename = ":memory:"):
        cur = self.getCursor()
        cur.execute("PRAGMA foreign_keys = ON;")

        cur.execute('PRAGMA synchronous = OFF')
        cur.execute('PRAGMA LOCKING_MODE = EXCLUSIVE')
        #self.cur.execute('PRAGMA journal_mode = MEMORY')
        #self.cur.execute('PRAGMA journal_mode = WAL')
        cur.execute("BEGIN TRANSACTION;")
        for item in SCHEMA:
            #print(item)
            res = cur.execute(item)
        self.conn.commit()

    def lastInsertedRowId(self, cur, table):
        rowid = cur.lastrowid
        result = cur.execute("SELECT DB_ID FROM {} WHERE rowid = ?".format(table), [rowid]).fetchone()
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

    def insertValues(self, tree):
        cur = self.getCursor()
        cur.execute("BEGIN TRANSACTION;")

        self.insertEnvironmentVariablesData(cur, tree['environmentVariablesData'])
        self.insertComments(cur, tree['comments'])
        self.insertValueTables(cur, tree['valueTables'])
        self.insertNodes(cur, tree['nodes'])
        self.insertMessages(cur, tree['messages'])
        self.insertEnvironmentVariables(cur, tree['environmentVariables'])

        self.insertValueDescriptions(cur, tree['valueDescriptions'])

        defaults = tree['attributeDefaults']
        self.insertAttributeDefinitions(cur, tree['attributeDefinitions'], defaults)
        self.conn.commit()

    def insertValueTables(self, cur, tables):
        for table in tables:
            name = table['name']
            description = table['description']
            cur.execute("""INSERT OR FAIL INTO Cdb_Valuetable(Name) VALUES(?)""", [name])
            res = cur.execute("SELECT DB_ID FROM Cdb_Valuetable WHERE Name = ?", [name]).fetchall()
            dbid = res[0][0]
            self.insertValueDescription(cur, dbid, description)

    def insertValueDescription(self, cur, dbid, description):
        for desc, value in description:
            cur.execute("""INSERT OR FAIL INTO Cdb_Value_Description(Valuetable, Value, Value_Description) VALUES(?, ?, ?)""", [dbid, value, desc])

    def insertEnvironmentVariables(self, cur, vars):
        for var in vars:
            unit = var['unit']
            initialValue = var['initialValue']
            accessNodes = var['accessNodes']
            accessType = var['accessType']
            minimum = var['minimum']
            maximum = var['maximum']
            envId = var['envId']
            varType = var['varType']
            name = var['name']
            cmt = self.fetchComment('EV', name)
            dataSize = self.fetchEnvironmentVariablesData(name)

            cur.execute("""INSERT OR FAIL INTO Cdb_EnvVar(Name, Type, Unit, Minimum, Maximum, Access, Startup_Value, Comment, Size)
                VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)""", [name, varType, unit, minimum, maximum, accessType, initialValue, cmt, dataSize]
            )
        print("-" * 80)

    def insertValueDescriptions(self, cur, descriptions):
        for item in descriptions:
            tp = item['type']
            description = item['description']
            if tp == 'SG':
                messageID = item['messageID']
                name = item['signalName']
                otype = 0
                dbid = cur.execute("""SELECT t1.db_id FROM cdb_signal AS t1, Cdb_Message_Signal AS t2 where
                    t1.db_id = t2.signal AND t1.name = ? AND t2.message = (SELECT db_id FROM cdb_message
                    WHERE message_id = ?)""", [name, messageID]
                ).fetchone()[0]
                #print("\tS-DB_ID", messageID, dbid, item, flush = True)
            elif tp == 'EV':
                name = item['envVarName']
                otype = 1
                dbid = cur.execute("SELECT DB_ID FROM Cdb_EnvVar WHERE name = ?", [name]).fetchone()[0]
                print("\tE-DB_ID", dbid, item, flush = True)
            cur.execute("""INSERT OR FAIL INTO Cdb_Valuetable(Name) VALUES(?)""", [name])
            vtid = self.lastInsertedRowId(cur, "Cdb_Valuetable")
            cur.execute("INSERT OR FAIL INTO Cdb_Object_Valuetable(Object_Type, Object_DB_ID, Valuetable) VALUES(?, ?, ?)", [otype, dbid, vtid])
            self.insertValueDescription(cur, vtid, description)
        print("-" * 80)

    def fetchNodeId(self, name):
        cur = self.getCursor()
        cur.execute("""SELECT DB_ID FROM Cdb_Node WHERE Name = ?""", [name])
        result = cur.fetchone()[0]
        return result

    def fetchSignalReceivers(self, messageId, signalId):
        cur = self.getCursor()
        cur.execute("SELECT (SELECT name FROM Cdb_Node WHERE db_id=node) FROM Cdb_Node_RxSignal WHERE message=? and signal=?", [messageId, signalId])
        result = [x[0] for x in cur.fetchall()]
        return result

    def insertNodes(self, cur, nodes):
        cur.execute("""INSERT OR FAIL INTO Cdb_Node(db_id, Name) VALUES(?, ?)""", [0, "Vector__XXX"])
        for node in nodes:
            cmt = self.fetchComment('BO', node)
            res = cur.execute("""INSERT OR FAIL INTO Cdb_Node(Name, Comment) VALUES(?, ?)""", [node, cmt])

    def createDictFromRow(self, row, description):
        names = [d[0] for d in description]
        di = dict(zip(names, row))
        return di

    @property
    def nodeNames(self):
        cur = self.conn.cursor()
        res = cur.execute("""SELECT Name FROM Cdb_Node WHERE db_id > 0""", []).fetchall()
        res = [x[0] for x in res]
        return res

    def nodeName(self, nid):
        cur = self.conn.cursor()
        res = cur.execute("""SELECT Name FROM Cdb_Node WHERE DB_ID = ?""", [nid]).fetchall()
        return res[0][0]

    def signals(self, messageId):
        cur = self.conn.cursor()
        res = cur.execute("""SELECT * FROM cdb_message_signal AS t1, cdb_signal AS t2 WHERE t1.message = ? AND t1.signal = t2.db_id""", [messageId])
        while True:
            row = cur.fetchone()
            if row is None:
                raise StopIteration
            else:
                yield self.createDictFromRow(row, cur.description)

    def fetchFromTable(self, tname, columns = None, where = None, orderBy = None):
        cur = self.conn.cursor()
        whereClause = "" if not where else "WHERE {}".format(where)
        orderByClause = "" if not orderBy else "ORDER BY {}".format(orderBy)
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
        yield from self.fetchFromTable("Cdb_Message")

    def comments(self):
        yield from self.fetchFromTable("comments")

    def valueTablesGlobal(self):
        yield from self.fetchFromTable("Cdb_Valuetable", where = "db_id NOT IN (SELECT valuetable FROM Cdb_Object_Valuetable)")

    def attributeDefinitions(self):
        yield from self.fetchFromTable("Cdb_Attribute_Definition")

    def environmentVariables(self):
        yield from self.fetchFromTable("Cdb_EnvVar")

    def messageIdFromDbid(self, dbid):
        cur = self.conn.cursor()
        cur.execute("""SELECT t2.message_id FROM cdb_message_signal AS t1, cdb_Message AS t2 WHERE t1.signal = ? AND t1.message = t2.db_id""", [dbid])
        res = cur.fetchone()[0]
        #print("messageIdFromDbid", res)
        return res

    def valueTablesLocal(self):
        cur = self.conn.cursor()
        res = cur.execute("""SELECT * FROM Cdb_Object_Valuetable AS t1, Cdb_Valuetable AS t2 WHERE t1.valuetable=t2.db_id""", [])
        while True:
            row = cur.fetchone()
            if row is None:
                raise StopIteration
            else:
                vt = self.createDictFromRow(row, cur.description)
                if vt['Object_Type'] == 0:
                    messageId = self.messageIdFromDbid(vt['Object_DB_ID'])
                    vt['Message_ID'] = messageId
                yield vt

    def valueDescription(self, tableId, srt = True):
        orderBy = "value desc" if srt else None
        yield from self.fetchFromTable("Cdb_Value_Description", where = "Valuetable = {}".format(tableId), orderBy = orderBy)

    def insertMessages(self, cur, messages):
        """
        CREATE TABLE Cdb_Message (
            DB_ID INTEGER NOT NULL DEFAULT 0,
            Name VARCHAR(255) NOT NULL,
            Message_ID INTEGER NOT NULL DEFAULT 0,
            Message_Format INTEGER NOT NULL DEFAULT 0,
            DLC INTEGER DEFAULT 0,
            Transmission_Type INTEGER DEFAULT 0,
            Cycletime INTEGER DEFAULT 0,
            Sender INTEGER DEFAULT 0,
            "Comment" VARCHAR(255),
            PRIMARY KEY(DB_ID)
        );
        CREATE TABLE Cdb_Signal (
            DB_ID INTEGER NOT NULL DEFAULT 0,
            Name VARCHAR(255) NOT NULL,
            Bitsize INTEGER DEFAULT 0,
            Byteorder INTEGER DEFAULT 0,
            Valuetype INTEGER DEFAULT 0,
            Initialvalue FLOAT8 DEFAULT 0,
            Formula_Factor FLOAT8 DEFAULT 1,
            Formula_Offset FLOAT8 DEFAULT 0,
            Minimum FLOAT8 DEFAULT 0,
            Maximum FLOAT8 DEFAULT 0,
            Unit VARCHAR(255),
            "Comment" VARCHAR(255),
            PRIMARY KEY(DB_ID)
        );
        """
        for msg in messages:
            name = msg['name']
            mid = msg['messageID']
            # 0xCFFFFFFF
            dlc = msg['dlc']
            signals = msg['signals']
            cmt = self.fetchComment('BO', mid)

            transmitter = msg['transmitter']
            tid = self.fetchNodeId(transmitter)

            res  = cur.execute("INSERT OR FAIL INTO Cdb_Message(Name, Message_ID, DLC, Comment, Sender) VALUES(?, ?, ?, ?, ?)",
                [name, mid, dlc, cmt, tid]
            )
            mdbid = self.lastInsertedRowId(cur, "Cdb_Message")
            for signal in signals:
                name = signal['name']
                startBit = signal['startBit']
                signalSize = signal['signalSize']
                byteOrder = signal['byteOrder']
                valueType = signal['valueType']
                factor = signal['factor']
                offset = signal['offset']
                minimum = signal['minimum']
                maximum = signal['maximum']
                unit = signal['unit']
                receiver = signal['receiver']
                multiplexerIndicator = signal['multiplexerIndicator']
                if multiplexerIndicator:
                    multiplexorSignal = 1 if multiplexerIndicator == 'M' else 0
                    if multiplexorSignal:
                        multiplexDependent = 0
                        multiplexorValue = None
                    else:
                        multiplexDependent = 1
                        multiplexorValue = int(multiplexerIndicator[1 : ])
                else:
                    multiplexorSignal = None
                    multiplexDependent = None
                    multiplexorValue = None
                initialValue = 0.0
                cmt = self.fetchComment('SG', mid, name)
                res = cur.execute(""" INSERT OR FAIL INTO Cdb_Signal(Name, Bitsize, Byteorder, Valuetype, Initialvalue, Formula_Factor,
                    Formula_Offset, Minimum, Maximum, Unit, Comment) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, [name, signalSize, byteOrder, valueType, initialValue, factor, offset, minimum, maximum, unit, cmt])
                sdbid = self.lastInsertedRowId(cur, "Cdb_Signal")

                # select * from cdb_message_signal where message = (select db_id from cdb_message where message_id = 2566843134);
                #
                # select * from cdb_signal where db_id in (select signal from cdb_message_signal where message =
                # (select db_id from cdb_message where message_id = 2566843134));

                cur.execute(""" INSERT OR FAIL INTO Cdb_Message_Signal(Message, Signal, Offset,
                    Multiplexor_Signal, Multiplex_Dependent, Multiplexor_Value) VALUES(?, ?, ?, ?, ?, ?)""",
                    [mdbid, sdbid, startBit, multiplexorSignal, multiplexDependent, multiplexorValue]
                )
                self.insertReceivers(cur, mdbid, sdbid, receiver)

    def insertReceivers(self, cur, messageId, signalId, receiver):
        for rcv in receiver:
            nodeId = self.fetchNodeId(rcv)
            cur.execute("INSERT OR FAIL INTO Cdb_Node_RxSignal(Message, Signal, Node) VALUES(?, ?, ?)", [messageId, signalId, nodeId])


    def insertComments(self, cur, comments):
        for comment in comments:
            tp = comment['type']
            text = comment['comment']
            key = comment['key']
            k0 = k1 = None
            if tp == 'BU':
                k0 = key
            elif tp == 'BO':
                k0 = key
            elif tp == 'SG':
                k0 = key[0]
                k1 = key[1]
            elif tp == 'EV':
                k0 = key
            res = cur.execute("""
                INSERT OR FAIL INTO comments(type, k0, k1, comment) VALUES(?, ?, ?, ?)
            """, [tp, k0, k1, text])

    def insertEnvironmentVariablesData(self, cur, data):
        for item in data:
            name = item['name']
            value = item['value']
            print(name, value)
            cur.execute("INSERT OR FAIL INTO EnvironmentVariablesData(name, value) VALUES(?, ?)", [name, value])

    def insertAttributeDefinitions(self, cur, attrs, defaults):
        for attr in attrs:
            attrType = attr['type']
            name = attr['name']
            vt = attr['value']['type']
            values = attr['value']['value']
            minimum = None
            maximum = None
            enumvalues = None
            defaultNumber = None
            defaultString = None
            default = defaults[name] if name in defaults else None
            if attrType == 'BU_':
                objType = AttributeType.NODE
            elif attrType == 'BO_':
                objType = AttributeType.MESSAGE
            elif attrType == 'SG_':
                objType = AttributeType.SIGNAL
            elif attrType == 'EV_':
                objType = AttributeType.ENV_VAR
            elif attrType is None:
                objType = AttributeType.GENERAL
            if vt == 'INT':
                valueType = ValueType.INT
                minimum, maximum = values
                if default is not None:
                    defaultNumber = default
            elif vt == 'HEX':
                valueType = ValueType.HEX
                minimum, maximum = values
                if default is not None:
                    defaultNumber = default
            elif vt == 'FLOAT':
                valueType = ValueType.FLOAT
                minimum, maximum = values
                if default is not None:
                    defaultNumber = default
            elif vt == 'STRING':
                valueType = ValueType.STRING
                if default is not None:
                    defaultString = default
            elif vt == 'ENUM':
                valueType = ValueType.ENUM
                enumvalues = ';'.join(values)
                if default is not None:
                    defaultString = default
            cur.execute("""INSERT OR FAIL INTO Cdb_Attribute_Definition(Name, Objecttype, Valuetype, Minimum, Maximum,
                Enumvalues, Default_Number, Default_String) VALUES(?, ?, ?, ?, ?, ?, ?, ?)""",
                [name, objType, valueType, minimum, maximum, enumvalues, defaultNumber, defaultString]
            )
            print("ATTR:", attr)
        '''
            CREATE TABLE Cdb_Attribute_Definition (
                DB_ID INTEGER NOT NULL DEFAULT 0,
                Name VARCHAR(255) NOT NULL,
                Objecttype INTEGER NOT NULL DEFAULT 0,
                Valuetype INTEGER NOT NULL DEFAULT 0,
                Minimum FLOAT8 DEFAULT 0,
                Maximum FLOAT8 DEFAULT 0,
                Enumvalues VARCHAR(255),
                Default_Number FLOAT8 DEFAULT 0,
                Default_String VARCHAR(255),
                Column_Index INTEGER NOT NULL DEFAULT 0,
                "Comment" TEXT,
                PRIMARY KEY(DB_ID)
            );
        ''', '''
            CREATE TABLE Cdb_Attribute_Value (
                Object_ID INTEGER NOT NULL DEFAULT 0,
                Attribute_Definition INTEGER NOT NULL DEFAULT 0,
                Num_Value FLOAT8 DEFAULT 0,
                String_Value TEXT,
                PRIMARY KEY(Object_ID,Attribute_Definition),
                FOREIGN KEY(Attribute_Definition) REFERENCES Cdb_Attribute_Definition(DB_ID)
            );
        ''', '''
            CREATE TABLE Cdb_AttributeRel_Value (
                Object_ID INTEGER NOT NULL DEFAULT 0,
                Attribute_Definition INTEGER NOT NULL DEFAULT 0,
                Num_Value FLOAT8 DEFAULT 0,
                String_Value TEXT,
                Opt_Object_ID_1 INTEGER DEFAULT 0,
                Opt_Object_ID_2 INTEGER DEFAULT 0,
                BLOB_Value BLOB,
                PRIMARY KEY(Object_ID,Attribute_Definition,Opt_Object_ID_1,Opt_Object_ID_2),
                FOREIGN KEY(Attribute_Definition) REFERENCES Cdb_Attribute_Definition(DB_ID)
            );
        '''

