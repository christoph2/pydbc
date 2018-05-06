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

# EV_ EnvShowFriction: 1 [0|0] "" 0 6 DUMMY_NODE_VECTOR2 Vector__XXX;   WRITE
# EV_ EnvShowFriction: 1 [0|0] "" 0 6 DUMMY_NODE_VECTOR0 Vector__XXX;   UNEINGESCHRÄNKT
# EV_ EnvShowFriction: 1 [0|0] "" 0 6 DUMMY_NODE_VECTOR1 Vector__XXX;   READ
# EV_ EnvShowFriction: 1 [0|0] "" 0 6 DUMMY_NODE_VECTOR3 Vector__XXX;   R/W
#

# SG_ Channel : 22|2@1+ (1,0) [0|0] ""  xx

# SYSDBA, masterkey

from collections import namedtuple
from pprint import pprint
import sqlite3
import types


SCHEMA = ('''
    DROP TABLE IF EXISTS Cdb_Node;

    CREATE TABLE Cdb_Node (
        DB_ID INTEGER NOT NULL DEFAULT 0,
        Name VARCHAR(255) NOT NULL,
        Node_ID INTEGER DEFAULT 0,
        "Comment" VARCHAR(255),
        PRIMARY KEY(DB_ID)
    );
''', '''
    DROP TABLE IF EXISTS Cdb_Message;

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
''', '''
    DROP TABLE IF EXISTS  Cdb_Signal;

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
    DROP TABLE IF EXISTS Cdb_Attribute_Definition;

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
    DROP TABLE IF EXISTS Cdb_Attribute_Value;

    CREATE TABLE Cdb_Attribute_Value (
        Object_ID INTEGER NOT NULL DEFAULT 0,
        Attribute_Definition INTEGER NOT NULL DEFAULT 0,
        Num_Value FLOAT8 DEFAULT 0,
        String_Value TEXT,
        PRIMARY KEY(Object_ID,Attribute_Definition),
        FOREIGN KEY(Attribute_Definition) REFERENCES Cdb_Attribute_Definition(DB_ID)
    );
''', '''
    DROP TABLE IF EXISTS Cdb_AttributeRel_Value;

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
    DROP TABLE IF EXISTS Cdb_DB_Info;

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
    DROP TABLE IF EXISTS Cdb_ECU;

    CREATE TABLE Cdb_ECU (
        DB_ID INTEGER NOT NULL DEFAULT 0,
        Name VARCHAR(255),
        "Comment" VARCHAR(255),
        PRIMARY KEY(DB_ID)
    );
    CREATE UNIQUE INDEX Cdb_ECU_DB_ID ON Cdb_ECU(DB_ID );
''', '''
    DROP TABLE IF EXISTS Cdb_EnvVar;

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
    DROP TABLE IF EXISTS Cdb_ECU_EnvVar;

    CREATE TABLE Cdb_ECU_EnvVar (
        ECU INTEGER NOT NULL DEFAULT 0,
        EnvVar INTEGER NOT NULL DEFAULT 0,
        PRIMARY KEY(ECU,EnvVar),
        FOREIGN KEY(ECU) REFERENCES Cdb_ECU(DB_ID),
        FOREIGN KEY(EnvVar) REFERENCES Cdb_EnvVar(DB_ID)
    );

    CREATE INDEX Cdb_ECU_EnvVar_Cdb_ECU_EnvVarECU ON Cdb_ECU_EnvVar(ECU );
''', '''
    DROP TABLE IF EXISTS Cdb_ECU_Node;

    CREATE TABLE Cdb_ECU_Node (
        ECU INTEGER NOT NULL DEFAULT 0,
        Node INTEGER NOT NULL DEFAULT 0,
        PRIMARY KEY(ECU,Node),
        FOREIGN KEY(ECU) REFERENCES Cdb_ECU(DB_ID),
        FOREIGN KEY(Node) REFERENCES Cdb_Node(DB_ID)
    );

    CREATE INDEX Cdb_ECU_Node_Cdb_ECU_NodeECU ON Cdb_ECU_Node(ECU );
''', '''
    DROP TABLE IF EXISTS Cdb_Gateway_Signal;

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

    CREATE UNIQUE INDEX Cdb_Gateway_Signal_DB_ID ON Cdb_Gateway_Signal(DB_ID );
''', '''
    DROP TABLE IF EXISTS Cdb_Group;

    CREATE TABLE Cdb_Group (
        DB_ID INTEGER NOT NULL DEFAULT 0,
        Name VARCHAR(255) NOT NULL,
        Object_Type INTEGER NOT NULL DEFAULT 0,
        Group_Type INTEGER NOT NULL DEFAULT 0,
        "Comment" VARCHAR(255),
        PRIMARY KEY(DB_ID)
    );
''', '''
    DROP TABLE IF EXISTS Cdb_Group_Object;

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

    CREATE INDEX Cdb_Group_Object_Group_DB_ID ON Cdb_Group_Object(Parent_DB_ID );
    CREATE INDEX Cdb_Group_Object_Object_DB_ID ON Cdb_Group_Object(Object_DB_ID );
    CREATE INDEX Cdb_Group_Object_Object_DB_ID_2 ON Cdb_Group_Object(Object_DB_ID_2 );
    CREATE INDEX Cdb_Group_Object_Object_Type ON Cdb_Group_Object(Object_Type );
    CREATE INDEX Cdb_Group_Object_Parent_Type ON Cdb_Group_Object(Parent_Type );
''', '''
    DROP TABLE IF EXISTS Cdb_Message_Signal;

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
    DROP TABLE IF EXISTS Cdb_Network;

    CREATE TABLE Cdb_Network (
        DB_ID INTEGER NOT NULL DEFAULT 0,
        Name VARCHAR(255) NOT NULL,
        "Comment" VARCHAR(255),
        Protocol INTEGER NOT NULL DEFAULT 0,
        Baudrate INTEGER DEFAULT 0,
        PRIMARY KEY(DB_ID)
    );

    CREATE UNIQUE INDEX Cdb_Network_DB_ID ON Cdb_Network(DB_ID );
''', '''
    DROP TABLE IF EXISTS Cdb_Network_Node;

    CREATE TABLE Cdb_Network_Node (
        Network INTEGER NOT NULL DEFAULT 0,
        Node INTEGER NOT NULL DEFAULT 0,
        PRIMARY KEY(Network,Node),
        FOREIGN KEY(Network) REFERENCES Cdb_Network(DB_ID),
        FOREIGN KEY(Node) REFERENCES Cdb_Node(DB_ID)
    );
''', '''
    DROP TABLE IF EXISTS Cdb_Node_RxSig;

    CREATE TABLE Cdb_Node_RxSig (
        Node INTEGER NOT NULL DEFAULT 0,
        Signal INTEGER NOT NULL DEFAULT 0,
        PRIMARY KEY(Node,Signal),
        FOREIGN KEY(Node) REFERENCES Cdb_Node(DB_ID),
        FOREIGN KEY(Signal) REFERENCES Cdb_Signal(DB_ID)
    );
''', '''
    DROP TABLE IF EXISTS Cdb_Node_RxSignal;

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
    DROP TABLE IF EXISTS Cdb_Node_TxMessage;

    CREATE TABLE Cdb_Node_TxMessage (
        Node INTEGER NOT NULL DEFAULT 0,
        Message INTEGER NOT NULL DEFAULT 0,
        PRIMARY KEY(Node,Message),
        FOREIGN KEY(Message) REFERENCES Cdb_Message(DB_ID),
        FOREIGN KEY(Node) REFERENCES Cdb_Node(DB_ID)
    );
''', '''
    DROP TABLE IF EXISTS Cdb_Node_TxSig;

    CREATE TABLE Cdb_Node_TxSig (
        Node INTEGER NOT NULL DEFAULT 0,
        Signal INTEGER NOT NULL DEFAULT 0,
        PRIMARY KEY(Node,Signal),
        FOREIGN KEY(Node) REFERENCES Cdb_Node(DB_ID),
        FOREIGN KEY(Signal) REFERENCES Cdb_Signal(DB_ID)
    );
''', '''
    DROP TABLE IF EXISTS Cdb_Object_Valuetable;

    CREATE TABLE Cdb_Object_Valuetable (
        Object_Type INTEGER NOT NULL DEFAULT 0,
        Object_DB_ID INTEGER NOT NULL DEFAULT 0,
        Valuetable INTEGER NOT NULL DEFAULT 0,
        PRIMARY KEY(Object_Type,Object_DB_ID),
        FOREIGN KEY(Valuetable) REFERENCES Cdb_Valuetable(DB_ID)
    );

    CREATE INDEX Cdb_Object_Valuetable_Object_DB_ID ON Cdb_Object_Valuetable(Object_DB_ID );
    CREATE INDEX Cdb_Object_Valuetable_Object_Type ON Cdb_Object_Valuetable(Object_Type );
''', '''
    DROP TABLE IF EXISTS Cdb_Value_Description;

    CREATE TABLE Cdb_Value_Description (
        Valuetable INTEGER NOT NULL DEFAULT 0,
        Value FLOAT8 NOT NULL DEFAULT 0,
        Value_Description VARCHAR(255) NOT NULL,
        PRIMARY KEY(Valuetable,Value),
        FOREIGN KEY(Valuetable) REFERENCES Cdb_Valuetable(DB_ID)
    );
''', '''
    DROP TABLE IF EXISTS Cdb_Valuetable;

    CREATE TABLE Cdb_Valuetable (
        DB_ID INTEGER NOT NULL DEFAULT 0,
        Name VARCHAR(255) NOT NULL,
        "Comment" VARCHAR(255),
        PRIMARY KEY(DB_ID)
    );
''', '''
    DROP TABLE IF EXISTS Cdb_Vehicle;

    CREATE TABLE Cdb_Vehicle (
        DB_ID INTEGER NOT NULL DEFAULT 0,
        Name VARCHAR(255) NOT NULL,
        "Comment" VARCHAR(255),
        PRIMARY KEY(DB_ID)
    );

    CREATE UNIQUE INDEX Cdb_Vehicle_DB_ID ON Cdb_Vehicle(DB_ID );
''', '''
    DROP TABLE IF EXISTS Cdb_Vehicle_ECU;

    CREATE TABLE Cdb_Vehicle_ECU (
        Vehicle INTEGER NOT NULL DEFAULT 0,
        ECU INTEGER NOT NULL DEFAULT 0,
        PRIMARY KEY(Vehicle,ECU),
        FOREIGN KEY(ECU) REFERENCES Cdb_ECU(DB_ID),
        FOREIGN KEY(Vehicle) REFERENCES Cdb_Vehicle(DB_ID)
    );
''', '''
    DROP TABLE IF EXISTS Cdb_Vehicle_Network;

    CREATE TABLE Cdb_Vehicle_Network (
        Vehicle INTEGER NOT NULL DEFAULT 0,
        Network INTEGER NOT NULL DEFAULT 0,
        PRIMARY KEY(Vehicle,Network),
        FOREIGN KEY(Network) REFERENCES Cdb_Network(DB_ID),
        FOREIGN KEY(Vehicle) REFERENCES Cdb_Vehicle(DB_ID)
    );
''', '''
    DROP TABLE IF EXISTS Cdb_Versioninfo;

    CREATE TABLE Cdb_Versioninfo (
        Obj_Type INTEGER NOT NULL DEFAULT 0,
        Obj_DB_ID INTEGER NOT NULL DEFAULT 0,
        Version_Number INTEGER NOT NULL DEFAULT 0,
        Is_Modified BOOLEAN NOT NULL,
        PRIMARY KEY(Obj_Type,Obj_DB_ID)
    );
''', '''
    DROP VIEW IF EXISTS schema;

    CREATE VIEW schema AS SELECT * FROM sqlite_master;
''', '''
    DROP TABLE IF EXISTS comments;

    CREATE TABLE comments(
        id INTEGER NOT NULL DEFAULT 0,
        type CHAR(16),
        k0 CHAR(32),
        k1 CHAR(32),
        comment BLOB,
        PRIMARY KEY(id)
    );
''')

FKS = '''
--
-- ***************************************************************************
-- *                                                                         *
-- *                               FOREIGN-KEYS                              *
-- *                                                                         *
-- ***************************************************************************
--
ALTER TABLE Cdb_Attribute_Value ADD CONSTRAINT Cdb_Attribute_DefinitionCdb_Attribute_Value FOREIGN KEY(Attribute_Definition) REFERENCES Cdb_Attribute_Definition(DB_ID);
ALTER TABLE Cdb_AttributeRel_Value ADD CONSTRAINT Cdb_Attribute_DefinitionCdb_AttributeRel_Value FOREIGN KEY(Attribute_Definition) REFERENCES Cdb_Attribute_Definition(DB_ID);
ALTER TABLE Cdb_ECU_EnvVar ADD CONSTRAINT Cdb_ECUCdb_ECU_EnvVar FOREIGN KEY(ECU) REFERENCES Cdb_ECU(DB_ID);
ALTER TABLE Cdb_ECU_EnvVar ADD CONSTRAINT Cdb_EnvVarCdb_ECU_EnvVar FOREIGN KEY(EnvVar) REFERENCES Cdb_EnvVar(DB_ID);
ALTER TABLE Cdb_ECU_Node ADD CONSTRAINT Cdb_ECUCdb_ECU_Node FOREIGN KEY(ECU) REFERENCES Cdb_ECU(DB_ID);
ALTER TABLE Cdb_ECU_Node ADD CONSTRAINT Cdb_NodeCdb_ECU_Node FOREIGN KEY(Node) REFERENCES Cdb_Node(DB_ID);
ALTER TABLE Cdb_Message_Signal ADD CONSTRAINT Cdb_MessageCdb_Message_Signal FOREIGN KEY(Message) REFERENCES Cdb_Message(DB_ID);
ALTER TABLE Cdb_Message_Signal ADD CONSTRAINT Cdb_SignalCdb_Message_Signal FOREIGN KEY(Signal) REFERENCES Cdb_Signal(DB_ID);
ALTER TABLE Cdb_Network_Node ADD CONSTRAINT Cdb_NetworkCdb_Network_Node FOREIGN KEY(Network) REFERENCES Cdb_Network(DB_ID);
ALTER TABLE Cdb_Network_Node ADD CONSTRAINT Cdb_NodeCdb_Network_Node FOREIGN KEY(Node) REFERENCES Cdb_Node(DB_ID);
ALTER TABLE Cdb_Node_RxSig ADD CONSTRAINT Cdb_NodeCdb_Node_RxSig FOREIGN KEY(Node) REFERENCES Cdb_Node(DB_ID);
ALTER TABLE Cdb_Node_RxSig ADD CONSTRAINT Cdb_SignalCdb_Node_RxSig FOREIGN KEY(Signal) REFERENCES Cdb_Signal(DB_ID);
ALTER TABLE Cdb_Node_RxSignal ADD CONSTRAINT Cdb_MessageCdb_Node_RxSignal FOREIGN KEY(Message) REFERENCES Cdb_Message(DB_ID);
ALTER TABLE Cdb_Node_RxSignal ADD CONSTRAINT Cdb_NodeCdb_Node_RxSignal FOREIGN KEY(Node) REFERENCES Cdb_Node(DB_ID);
ALTER TABLE Cdb_Node_RxSignal ADD CONSTRAINT Cdb_SignalCdb_Node_RxSignal FOREIGN KEY(Signal) REFERENCES Cdb_Signal(DB_ID);
ALTER TABLE Cdb_Node_TxMessage ADD CONSTRAINT Cdb_MessageCdb_Node_TxMessage FOREIGN KEY(Message) REFERENCES Cdb_Message(DB_ID);
ALTER TABLE Cdb_Node_TxMessage ADD CONSTRAINT Cdb_NodeCdb_Node_TxMessage FOREIGN KEY(Node) REFERENCES Cdb_Node(DB_ID);
ALTER TABLE Cdb_Node_TxSig ADD CONSTRAINT Cdb_NodeCdb_Node_TxSig FOREIGN KEY(Node) REFERENCES Cdb_Node(DB_ID);
ALTER TABLE Cdb_Node_TxSig ADD CONSTRAINT Cdb_SignalCdb_Node_TxSig FOREIGN KEY(Signal) REFERENCES Cdb_Signal(DB_ID);
ALTER TABLE Cdb_Object_Valuetable ADD CONSTRAINT Cdb_ValuetableCdb_Object_Valuetable FOREIGN KEY(Valuetable) REFERENCES Cdb_Valuetable(DB_ID);
ALTER TABLE Cdb_Value_Description ADD CONSTRAINT Cdb_ValuetableCdb_Value_Description FOREIGN KEY(Valuetable) REFERENCES Cdb_Valuetable(DB_ID);
ALTER TABLE Cdb_Vehicle_ECU ADD CONSTRAINT Cdb_ECUCdb_Vehicle_ECU FOREIGN KEY(ECU) REFERENCES Cdb_ECU(DB_ID);
ALTER TABLE Cdb_Vehicle_ECU ADD CONSTRAINT Cdb_VehicleCdb_Vehicle_ECU FOREIGN KEY(Vehicle) REFERENCES Cdb_Vehicle(DB_ID);
ALTER TABLE Cdb_Vehicle_Network ADD CONSTRAINT Cdb_NetworkCdb_Vehicle_Network FOREIGN KEY(Network) REFERENCES Cdb_Network(DB_ID);
ALTER TABLE Cdb_Vehicle_Network ADD CONSTRAINT Cdb_VehicleCdb_Vehicle_Network FOREIGN KEY(Vehicle) REFERENCES Cdb_Vehicle(DB_ID);
'''

class CanDatabase(object):

    def __init__(self, filename = ":memory:"):
        self.conn = sqlite3.connect(filename)
        self.conn.isolation_level = None
        self.cur = self.conn.cursor()
        self.filename = filename
        self.createSchema(filename)

    def __del__(self):
        self.cur.close()
        self.conn.close()

    def createSchema(self, filename = ":memory:"):
        self.cur.execute("PRAGMA foreign_keys = ON;")
        for item in SCHEMA:
            #print(item)
            res = self.cur.executescript(item)
        self.conn.commit()

        self.cur.execute("SELECT sql FROM sqlite_master")
        #cur.execute("pragma table_info(Cdb_Vehicle_Network)")
        res = self.cur.fetchall()
        #pprint(res)


    def insertValues(self, tree):
        """OrderedDict(messageID, name, dlc, transmitter, signals)

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
        ctx.value = OrderedDict(name = ctx.signalName.text, startBit = self.getInt(ctx.startBit), signalSize = self.getInt(ctx.signalSize),
            byteOrder = ctx.byteOrder.text, valueType = -1 if ctx.valueType.text == '-' else +1, factor = ctx.factor.value, offset = ctx.offset.value,
            minimum = ctx.minimum.value, maximum = ctx.maximum.value, unit = ctx.unit.text, receiver = ctx.rcv.value,
            multiplexerIndicator = ctx.mind.value if ctx.mind else None
        )
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
        self.cur.execute("BEGIN TRANSACTION;")
        for comment in tree['comments']:
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
            #print(comment)
            res = self.cur.execute("""
                INSERT INTO comments(type, k0, k1, comment) VALUES(?, ?, ?, ?)
            """, [tp, k0, k1, text])
        messages = tree['messages']
        for msg in messages:

            self.cur.execute("SELECT comment FROM comments WHERE type = 'BO' AND k0 = ?;", [msg['messageID']])
            res = self.cur.fetchall()
            assert len(res[0]) <= 1

            res  = self.cur.execute("INSERT INTO Cdb_Message(Name, Message_ID, DLC, Comment) VALUES(?, ?, ?, ?)",
                [msg['name'], msg['messageID'], msg['dlc'], res[0][0]]
            )
            for signal in msg['signals']:
                #pprint(signal)
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
                initialValue = 0.0
                res = self.cur.execute(""" INSERT INTO Cdb_Signal(Name, Bitsize, Byteorder, Valuetype, Initialvalue, Formula_Factor,
                    Formula_Offset, Minimum, Maximum, Unit) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, [name, signalSize, byteOrder, valueType, initialValue, factor, offset, minimum, maximum, unit])
            #print("=" * 80)
        self.conn.commit()

