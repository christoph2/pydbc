#!/usr/bin/env python
# -*- coding: utf-8 -*-

__copyright__ = """
   pySART - Simplified AUTOSAR-Toolkit for Python.

   (C) 2010-2018 by Christoph Schueler <cpu12.gems@googlemail.com>

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
__version__ = '0.9.0'


from collections import namedtuple
from pprint import pprint
import sqlite3
import types


# http://www.webshop-factory.com/shopsysteme
# https://www.fuer-gruender.de/meine-firma/logo-website/

"""
    •ConCardis
    •Sage Pay
    •PAYONE
    •Wirecard
    •mPAY24
    •Six Card Solutions
    •Heidelpay
    •Secupay
    •Novalnet
    •BillPay
"""

INDICES = (
    "CREATE UNIQUE INDEX Cdb_ECU_DB_ID ON Cdb_ECU(DB_ID );",
    "CREATE INDEX Cdb_ECU_EnvVar_Cdb_ECU_EnvVarECU ON Cdb_ECU_EnvVar(ECU );",
    "CREATE INDEX Cdb_ECU_Node_Cdb_ECU_NodeECU ON Cdb_ECU_Node(ECU );",
    "CREATE UNIQUE INDEX Cdb_Gateway_Signal_DB_ID ON Cdb_Gateway_Signal(DB_ID );",
    "CREATE INDEX Cdb_Group_Object_Group_DB_ID ON Cdb_Group_Object(Parent_DB_ID );",
    "CREATE INDEX Cdb_Group_Object_Object_DB_ID ON Cdb_Group_Object(Object_DB_ID );",
    "CREATE INDEX Cdb_Group_Object_Object_DB_ID_2 ON Cdb_Group_Object(Object_DB_ID_2 );",
    "CREATE INDEX Cdb_Group_Object_Object_Type ON Cdb_Group_Object(Object_Type );",
    "CREATE INDEX Cdb_Group_Object_Parent_Type ON Cdb_Group_Object(Parent_Type );",
    "CREATE UNIQUE INDEX Cdb_Network_DB_ID ON Cdb_Network(DB_ID );",
    "CREATE INDEX Cdb_Object_Valuetable_Object_DB_ID ON Cdb_Object_Valuetable(Object_DB_ID );",
    "CREATE INDEX Cdb_Object_Valuetable_Object_Type ON Cdb_Object_Valuetable(Object_Type );",
    "CREATE UNIQUE INDEX Cdb_Vehicle_DB_ID ON Cdb_Vehicle(DB_ID );",
)

DROP_TABLES = (
    "DROP TABLE IF EXISTS Cdb_Message_Signal;",
    "DROP TABLE IF EXISTS Cdb_ECU_Node;",
    "DROP TABLE IF EXISTS Cdb_Network_Node;",
    "DROP TABLE IF EXISTS Cdb_Node_RxSig;",
    "DROP TABLE IF EXISTS Cdb_Node_RxSignal;",
    "DROP TABLE IF EXISTS Cdb_Node_TxMessage;",
    "DROP TABLE IF EXISTS Cdb_Node_TxSig;",
    "DROP TABLE IF EXISTS Cdb_Node;",
    "DROP TABLE IF EXISTS Cdb_Message;",
    "DROP TABLE IF EXISTS Cdb_Signal;",
    "DROP TABLE IF EXISTS Cdb_Attribute_Value;",
    "DROP TABLE IF EXISTS Cdb_AttributeRel_Value;",
    "DROP TABLE IF EXISTS Cdb_Attribute_Definition;",
    "DROP TABLE IF EXISTS Cdb_DB_Info;",
    "DROP TABLE IF EXISTS Cdb_ECU_EnvVar;",
    "DROP TABLE IF EXISTS Cdb_ECU;",
    "DROP TABLE IF EXISTS Cdb_EnvVar;",
    "DROP TABLE IF EXISTS Cdb_Gateway_Signal;",
    "DROP TABLE IF EXISTS Cdb_Group;",
    "DROP TABLE IF EXISTS Cdb_Group_Object;",
    "DROP TABLE IF EXISTS Cdb_Network;",
    "DROP TABLE IF EXISTS Cdb_Object_Valuetable;",
    "DROP TABLE IF EXISTS Cdb_Value_Description;",
    "DROP TABLE IF EXISTS Cdb_Valuetable;",
    "DROP TABLE IF EXISTS Cdb_Vehicle;",
    "DROP TABLE IF EXISTS Cdb_Vehicle_Network;",
    "DROP TABLE IF EXISTS Cdb_Vehicle_ECU;",
    "DROP TABLE IF EXISTS Cdb_Versioninfo;",
    "DROP VIEW IF EXISTS schema;",
    "DROP TABLE IF EXISTS comments;",
    "DROP TABLE IF EXISTS EnvironmentVariablesData;",
)

SCHEMA = ('''
    CREATE TABLE Cdb_Node (
        DB_ID INTEGER NOT NULL DEFAULT 0,
        Name VARCHAR(255) NOT NULL,
        Node_ID INTEGER DEFAULT 0,
        "Comment" VARCHAR(255),
        PRIMARY KEY(DB_ID)
    );
''', '''
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
        PRIMARY KEY(DB_ID),
        UNIQUE(Name),
        UNIQUE(Message_ID)
    );
''', '''
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
''', '''
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
''', '''
    CREATE TABLE Cdb_DB_Info (
        DB_Schema_Version INTEGER DEFAULT 2,
        Req_DB_Editor_Version INTEGER DEFAULT 1,
        Report_DB_Filename VARCHAR(255),
        Report_Objecttype INTEGER DEFAULT 0,
        Report_Objectname VARCHAR(255),
        Display_Format_Motorola INTEGER DEFAULT 0,
        Display_Format_Intel INTEGER DEFAULT 0,
        Number_Format INTEGER DEFAULT 0,
        Number_Format_Hex_Attributes INTEGER DEFAULT 0,
        Number_Format_Int_Attributes INTEGER DEFAULT 0
    );
''', '''
    CREATE TABLE Cdb_ECU (
        DB_ID INTEGER NOT NULL DEFAULT 0,
        Name VARCHAR(255),
        "Comment" VARCHAR(255),
        PRIMARY KEY(DB_ID)
    );
''', '''
    CREATE TABLE Cdb_EnvVar (
        DB_ID INTEGER NOT NULL DEFAULT 0,
        Name VARCHAR(255) NOT NULL,
        Type INTEGER NOT NULL DEFAULT 0,
        Unit VARCHAR(255),
        Minimum FLOAT8 DEFAULT 0,
        Maximum FLOAT8 DEFAULT 0,
        Startup_Value FLOAT8 DEFAULT 0,
        Size INTEGER DEFAULT 0,
        "Access" INTEGER DEFAULT 0,
        "Comment" VARCHAR(255),
        PRIMARY KEY(DB_ID)
    );
''', '''
    CREATE TABLE Cdb_ECU_EnvVar (
        ECU INTEGER NOT NULL DEFAULT 0,
        EnvVar INTEGER NOT NULL DEFAULT 0,
        PRIMARY KEY(ECU,EnvVar),
        FOREIGN KEY(ECU) REFERENCES Cdb_ECU(DB_ID),
        FOREIGN KEY(EnvVar) REFERENCES Cdb_EnvVar(DB_ID)
    );
''', '''
    CREATE TABLE Cdb_ECU_Node (
        ECU INTEGER NOT NULL DEFAULT 0,
        Node INTEGER NOT NULL DEFAULT 0,
        PRIMARY KEY(ECU,Node),
        FOREIGN KEY(ECU) REFERENCES Cdb_ECU(DB_ID),
        FOREIGN KEY(Node) REFERENCES Cdb_Node(DB_ID)
    );
''', '''
    CREATE TABLE Cdb_Gateway_Signal (
        DB_ID INTEGER NOT NULL DEFAULT 0,
        Vehicle_ID INTEGER NOT NULL DEFAULT 0,
        Dest_Signal INTEGER NOT NULL DEFAULT 0,
        Dest_Network INTEGER NOT NULL DEFAULT 0,
        Dest_Message INTEGER NOT NULL DEFAULT 0,
        Dest_Transmitter INTEGER NOT NULL DEFAULT 0,
        Gateway_ECU INTEGER NOT NULL DEFAULT 0,
        Source_Signal INTEGER NOT NULL DEFAULT 0,
        Source_Network INTEGER NOT NULL DEFAULT 0,
        Source_Message INTEGER NOT NULL DEFAULT 0,
        Source_Receiver INTEGER NOT NULL DEFAULT 0,
        "Comment" VARCHAR(255),
        Reserved_ID1 INTEGER NOT NULL DEFAULT 0,
        PRIMARY KEY(DB_ID)
    );
''', '''
    CREATE TABLE Cdb_Group (
        DB_ID INTEGER NOT NULL DEFAULT 0,
        Name VARCHAR(255) NOT NULL,
        Object_Type INTEGER NOT NULL DEFAULT 0,
        Group_Type INTEGER NOT NULL DEFAULT 0,
        "Comment" VARCHAR(255),
        PRIMARY KEY(DB_ID)
    );
''', '''
    CREATE TABLE Cdb_Group_Object (
        Parent_Type INTEGER NOT NULL DEFAULT 0,
        Parent_DB_ID INTEGER NOT NULL DEFAULT 0,
        Object_Type INTEGER NOT NULL DEFAULT 0,
        Object_DB_ID INTEGER NOT NULL DEFAULT 0,
        Object_DB_ID_2 INTEGER NOT NULL DEFAULT 0,
        Opt_Object_Ref_1 INTEGER DEFAULT 0,
        Opt_Object_Ref_2 INTEGER DEFAULT 0,
        Opt_Object_Value INTEGER DEFAULT 0,
        PRIMARY KEY(Parent_Type,Parent_DB_ID,Object_Type,Object_DB_ID,Object_DB_ID_2)
    );
''', '''
    CREATE TABLE Cdb_Message_Signal (
        Message INTEGER NOT NULL DEFAULT 0,
        Signal INTEGER NOT NULL DEFAULT 0,
        "Offset" INTEGER NOT NULL DEFAULT 0,
        Multiplexor_Signal SMALLINT,
        Multiplex_Dependent SMALLINT,
        Multiplexor_Value INTEGER,
        PRIMARY KEY(Message,Signal),
        FOREIGN KEY(Message) REFERENCES Cdb_Message(DB_ID),
        FOREIGN KEY(Signal) REFERENCES Cdb_Signal(DB_ID)
    );
''', '''
    CREATE TABLE Cdb_Network (
        DB_ID INTEGER NOT NULL DEFAULT 0,
        Name VARCHAR(255) NOT NULL,
        "Comment" VARCHAR(255),
        Protocol INTEGER NOT NULL DEFAULT 0,
        Baudrate INTEGER DEFAULT 0,
        PRIMARY KEY(DB_ID)
    );
''', '''
    CREATE TABLE Cdb_Network_Node (
        Network INTEGER NOT NULL DEFAULT 0,
        Node INTEGER NOT NULL DEFAULT 0,
        PRIMARY KEY(Network,Node),
        FOREIGN KEY(Network) REFERENCES Cdb_Network(DB_ID),
        FOREIGN KEY(Node) REFERENCES Cdb_Node(DB_ID)
    );
''', '''
    CREATE TABLE Cdb_Node_RxSig (
        Node INTEGER NOT NULL DEFAULT 0,
        Signal INTEGER NOT NULL DEFAULT 0,
        PRIMARY KEY(Node,Signal),
        FOREIGN KEY(Node) REFERENCES Cdb_Node(DB_ID),
        FOREIGN KEY(Signal) REFERENCES Cdb_Signal(DB_ID)
    );
''', '''
    CREATE TABLE Cdb_Node_RxSignal (
        Node INTEGER NOT NULL DEFAULT 0,
        Message INTEGER NOT NULL DEFAULT 0,
        Signal INTEGER NOT NULL DEFAULT 0,
        PRIMARY KEY(Node,Message,Signal),
        FOREIGN KEY(Message) REFERENCES Cdb_Message(DB_ID),
        FOREIGN KEY(Node) REFERENCES Cdb_Node(DB_ID),
        FOREIGN KEY(Signal) REFERENCES Cdb_Signal(DB_ID)
    );
''', '''
    CREATE TABLE Cdb_Node_TxMessage (
        Node INTEGER NOT NULL DEFAULT 0,
        Message INTEGER NOT NULL DEFAULT 0,
        PRIMARY KEY(Node,Message),
        FOREIGN KEY(Message) REFERENCES Cdb_Message(DB_ID),
        FOREIGN KEY(Node) REFERENCES Cdb_Node(DB_ID)
    );
''', '''
    CREATE TABLE Cdb_Node_TxSig (
        Node INTEGER NOT NULL DEFAULT 0,
        Signal INTEGER NOT NULL DEFAULT 0,
        PRIMARY KEY(Node,Signal),
        FOREIGN KEY(Node) REFERENCES Cdb_Node(DB_ID),
        FOREIGN KEY(Signal) REFERENCES Cdb_Signal(DB_ID)
    );
''', '''
    CREATE TABLE Cdb_Object_Valuetable (
        Object_Type INTEGER NOT NULL DEFAULT 0,
        Object_DB_ID INTEGER NOT NULL DEFAULT 0,
        Valuetable INTEGER NOT NULL DEFAULT 0,
        PRIMARY KEY(Object_Type,Object_DB_ID),
        FOREIGN KEY(Valuetable) REFERENCES Cdb_Valuetable(DB_ID)
    );
''', '''
    CREATE TABLE Cdb_Value_Description (
        Valuetable INTEGER NOT NULL DEFAULT 0,
        Value FLOAT8 NOT NULL DEFAULT 0,
        Value_Description VARCHAR(255) NOT NULL,
        PRIMARY KEY(Valuetable,Value),
        FOREIGN KEY(Valuetable) REFERENCES Cdb_Valuetable(DB_ID)
    );
''', '''
    CREATE TABLE Cdb_Valuetable (
        DB_ID INTEGER NOT NULL DEFAULT 0,
        Name VARCHAR(255) NOT NULL,
        "Comment" VARCHAR(255),
        PRIMARY KEY(DB_ID)
    );
''', '''
    CREATE TABLE Cdb_Vehicle (
        DB_ID INTEGER NOT NULL DEFAULT 0,
        Name VARCHAR(255) NOT NULL,
        "Comment" VARCHAR(255),
        PRIMARY KEY(DB_ID)
    );
''', '''
    CREATE TABLE Cdb_Vehicle_ECU (
        Vehicle INTEGER NOT NULL DEFAULT 0,
        ECU INTEGER NOT NULL DEFAULT 0,
        PRIMARY KEY(Vehicle,ECU),
        FOREIGN KEY(ECU) REFERENCES Cdb_ECU(DB_ID),
        FOREIGN KEY(Vehicle) REFERENCES Cdb_Vehicle(DB_ID)
    );
''', '''
    CREATE TABLE Cdb_Vehicle_Network (
        Vehicle INTEGER NOT NULL DEFAULT 0,
        Network INTEGER NOT NULL DEFAULT 0,
        PRIMARY KEY(Vehicle,Network),
        FOREIGN KEY(Network) REFERENCES Cdb_Network(DB_ID),
        FOREIGN KEY(Vehicle) REFERENCES Cdb_Vehicle(DB_ID)
    );
''', '''
    CREATE TABLE Cdb_Versioninfo (
        Obj_Type INTEGER NOT NULL DEFAULT 0,
        Obj_DB_ID INTEGER NOT NULL DEFAULT 0,
        Version_Number INTEGER NOT NULL DEFAULT 0,
        Is_Modified BOOLEAN NOT NULL,
        PRIMARY KEY(Obj_Type,Obj_DB_ID)
    );
''', '''
    CREATE VIEW schema AS SELECT * FROM sqlite_master;
''', '''
    CREATE TABLE comments(
        id INTEGER NOT NULL DEFAULT 0,
        type CHAR(16),
        k0 CHAR(32),
        k1 CHAR(32),
        comment BLOB,
        PRIMARY KEY(id)
    );
''', '''
    CREATE TABLE EnvironmentVariablesData(
        name CHAR(256) NOT NULL,
        value INT NOT NULL,
        PRIMARY KEY(name)
    );
''')

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
        for item in DROP_TABLES:
            #print(item)
            res = cur.execute(item)
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
        self.conn.commit()

    def insertValueTables(self, cur, tables):
        for table in tables:
            name = table['name']
            description = table['description']
            cur.execute("""INSERT INTO Cdb_Valuetable(Name) VALUES(?)""", [name])
            res = cur.execute("SELECT DB_ID FROM Cdb_Valuetable WHERE Name = ?", [name]).fetchall()
            dbid = res[0][0]
            for desc, value in description:
                cur.execute("""INSERT INTO Cdb_Value_Description(Valuetable, Value, Value_Description) VALUES(?, ?, ?)""", [dbid, value, desc])

    def insertEnvironmentVariables(self, cur, vars):
        print("ENV-VARS")
        for var in vars:
            print(var)
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

            cur.execute("""INSERT INTO Cdb_EnvVar(Name, Type, Unit, Minimum, Maximum, Access, Startup_Value, Comment, Size)
                VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)""", [name, varType, unit, minimum, maximum, accessType, initialValue, cmt, dataSize]
            )
        print("-" * 80)

    def insertValueDescriptions(self, cur, descriptions):
        """
        CREATE TABLE Cdb_Object_Valuetable (
            Object_Type INTEGER NOT NULL DEFAULT 0,
            Object_DB_ID INTEGER NOT NULL DEFAULT 0,
            Valuetable INTEGER NOT NULL DEFAULT 0,
            PRIMARY KEY(Object_Type,Object_DB_ID),
            FOREIGN KEY(Valuetable) REFERENCES Cdb_Valuetable(DB_ID)
        );
        """
        for item in descriptions:
            #print(item)
            tp = item['type']
            description = item['description']
            if tp == 'SG':
                messageID = item['messageID']
                signalName = item['signalName']
                dbid = cur.execute("SELECT DB_ID FROM Cdb_Signal WHERE name = ?", [signalName]).fetchall()
                #print("\tS-DB_ID", dbid)
            elif tp == 'EV':
                envVarName = item['envVarName']
                dbid = cur.execute("SELECT DB_ID FROM Cdb_EnvVar WHERE name = ?", [envVarName]).fetchall()
                #print("\tE-DB_ID", dbid)

        print("-" * 80)

    def fetchNodeId(self, name):
        cur = self.getCursor()
        cur.execute("""SELECT DB_ID FROM Cdb_Node WHERE Name = ?""", [name])
        result = cur.fetchone()[0]
        return result

    def fetchSignalReceivers(self, messageId, signalId):
        cur = self.getCursor()
        cur.execute("""SELECT name FROM Cdb_Node WHERE db_id IN (SELECT node FROM Cdb_Node_RxSignal where message=? and signal=?)""",
            [messageId, signalId]
        )
        result = [x[0] for x in cur.fetchall()]
        return result

    def insertNodes(self, cur, nodes):
        cur.execute("""INSERT INTO Cdb_Node(db_id, Name) VALUES(?, ?)""", [0, "Vector__XXX"])
        for node in nodes:
            cmt = self.fetchComment('BO', node)
            res = cur.execute("""INSERT INTO Cdb_Node(Name, Comment) VALUES(?, ?)""", [node, cmt])

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
        """
         SG_ {'Multiplex_Dependent': None, 'Bitsize': 8, 'Multiplexor_Value': None, 'DB_ID': 4, 'Initialvalue': 0.0,
         'Maximum': 0.0, 'Minimum': 0.0, 'Name': 'Information', 'Valuetype': -1, 'Formula_Factor': 1.0, 'Byteorder': 1,
         'Comment': None, 'Signal': 4, 'Unit': '""', 'Offset': 0, 'Message': 5, 'Formula_Offset': 0.0, 'Multiplexor_Signal': None}
        """
        cur = self.conn.cursor()
        res = cur.execute("""select * from cdb_message_signal as t1, cdb_signal as t2 where t1.message = ? and t1.signal = t2.db_id""", [messageId])
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

    def messages(self):
        yield from self.fetchFromTable("Cdb_Message")

    def comments(self):
        yield from self.fetchFromTable("comments")

    def valueTables(self):
        yield from self.fetchFromTable("Cdb_Valuetable")

    def valueDescription(self, tableId):
        yield from self.fetchFromTable("Cdb_Value_Description", where = "Valuetable = {}".format(tableId), orderBy = "value desc")

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
        CREATE TABLE Cdb_Message_Signal (
            Message INTEGER NOT NULL DEFAULT 0,
            Signal INTEGER NOT NULL DEFAULT 0,
            "Offset" INTEGER NOT NULL DEFAULT 0,
            Multiplexor_Signal SMALLINT,
            Multiplex_Dependent SMALLINT,
            Multiplexor_Value INTEGER,
            PRIMARY KEY(Message,Signal),
            FOREIGN KEY(Message) REFERENCES Cdb_Message(DB_ID),
            FOREIGN KEY(Signal) REFERENCES Cdb_Signal(DB_ID)
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

            res  = cur.execute("INSERT INTO Cdb_Message(Name, Message_ID, DLC, Comment, Sender) VALUES(?, ?, ?, ?, ?)",
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
                res = cur.execute(""" INSERT INTO Cdb_Signal(Name, Bitsize, Byteorder, Valuetype, Initialvalue, Formula_Factor,
                    Formula_Offset, Minimum, Maximum, Unit, Comment) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, [name, signalSize, byteOrder, valueType, initialValue, factor, offset, minimum, maximum, unit, cmt])
                sdbid = self.lastInsertedRowId(cur, "Cdb_Signal")

                # select * from cdb_message_signal where message = (select db_id from cdb_message where message_id = 2566843134);
                #
                # select * from cdb_signal where db_id in (select signal from cdb_message_signal where message =
                # (select db_id from cdb_message where message_id = 2566843134));

                cur.execute(""" INSERT INTO Cdb_Message_Signal(Message, Signal, Offset,
                    Multiplexor_Signal, Multiplex_Dependent, Multiplexor_Value) VALUES(?, ?, ?, ?, ?, ?)""",
                    [mdbid, sdbid, startBit, multiplexorSignal, multiplexDependent, multiplexorValue]
                )
                self.insertReceivers(cur, mdbid, sdbid, receiver)

    def insertReceivers(self, cur, messageId, signalId, receiver):
        for rcv in receiver:
            nodeId = self.fetchNodeId(rcv)
            cur.execute("INSERT INTO Cdb_Node_RxSignal(Message, Signal, Node) VALUES(?, ?, ?)", [messageId, signalId, nodeId])


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
                INSERT INTO comments(type, k0, k1, comment) VALUES(?, ?, ?, ?)
            """, [tp, k0, k1, text])

    def insertEnvironmentVariablesData(self, cur, data):
        for item in data:
            name = item['name']
            value = item['value']
            print(name, value)
            cur.execute("INSERT INTO EnvironmentVariablesData(name, value) VALUES(?, ?)", [name, value])

