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

#  datetime('now', 'localtime')

INDICES = (
    "CREATE UNIQUE INDEX IF NOT EXISTS ECU_RID ON ECU(RID );",
    "CREATE INDEX IF NOT EXISTS ECU_EnvVar_ECU_EnvVarECU ON ECU_EnvVar(ECU );",
    "CREATE INDEX IF NOT EXISTS ECU_Node_ECU_NodeECU ON ECU_Node(ECU );",
    "CREATE UNIQUE INDEX IF NOT EXISTS Gateway_Signal_RID ON Gateway_Signal(RID );",
    "CREATE INDEX IF NOT EXISTS Node_Group_Object_Node_Group_RID ON Node_Group_Object(Parent_RID );",
    "CREATE INDEX IF NOT EXISTS Node_Group_Object_Object_RID ON Node_Group_Object(Object_RID );",
    "CREATE INDEX IF NOT EXISTS Node_Group_Object_Object_RID_2 ON Node_Group_Object(Object_RID_2 );",
    "CREATE INDEX IF NOT EXISTS Node_Group_Object_Object_Type ON Node_Group_Object(Object_Type );",
    "CREATE INDEX IF NOT EXISTS Node_Group_Object_Parent_Type ON Node_Group_Object(Parent_Type );",
    "CREATE UNIQUE INDEX IF NOT EXISTS Network_RID ON Network(RID );",
    "CREATE INDEX IF NOT EXISTS Object_Valuetable_Object_RID ON Object_Valuetable(Object_RID );",
    "CREATE INDEX IF NOT EXISTS Object_Valuetable_Object_Type ON Object_Valuetable(Object_Type );",
    "CREATE UNIQUE INDEX IF NOT EXISTS Vehicle_RID ON Vehicle(RID );",

    "CREATE UNIQUE INDEX IF NOT EXISTS Node_Name ON Node(Name)",
    "CREATE INDEX IF NOT EXISTS Signal_Name ON Signal(Name)",
)

TABLES = (
    "Message_Signal",
    "ECU_Node",
    "Network_Node",
    "Node_RxSig",
    "Node_RxSignal",
    "Node_TxMessage",
    "Node_TxSig",
    "Message",
    "Signal",
    "Attribute_Value",
    "AttributeRel_Value",
    "Attribute_Definition",
    "VndbMeta",
    "EnvVar_AccessNode",
    "ECU_EnvVar",
    "ECU",
    "EnvVar",
    "Gateway_Signal",
    "Node_Group",
    "Node_Group_Object",
    "Network",
    "Object_Valuetable",
    "Value_Description",
    "Valuetable",
    "Vehicle",
    "Vehicle_Network",
    "Vehicle_ECU",
    "Versioninfo",
    "comments",
    "EnvironmentVariablesData",

    "Node",
)

VIEWS = (
    "schema",
)

SCHEMA = ('''
    CREATE TABLE IF NOT EXISTS Node (
        RID INTEGER NOT NULL DEFAULT 0,
        Name VARCHAR(255) NOT NULL,
        Node_ID INTEGER DEFAULT 0,
        "Comment" VARCHAR(255),
        PRIMARY KEY(RID)
    );
''', '''
    CREATE TABLE IF NOT EXISTS Message (
        RID INTEGER NOT NULL DEFAULT 0,
        Name VARCHAR(255) NOT NULL,
        Message_ID INTEGER NOT NULL DEFAULT 0,
        DLC INTEGER DEFAULT 0,
        Sender INTEGER DEFAULT 0,
        "Comment" VARCHAR(255),
        PRIMARY KEY(RID),
        UNIQUE(Name),
        UNIQUE(Message_ID)
    );
''', '''
    CREATE TABLE IF NOT EXISTS Signal (
        RID INTEGER NOT NULL DEFAULT 0,
        Name VARCHAR(255) NOT NULL,
        Bitsize INTEGER DEFAULT 0,
        Byteorder INTEGER DEFAULT 1,
        Sign INTEGER DEFAULT 1,
        Valuetype INTEGER DEFAULT 0,
        Formula_Factor FLOAT8 DEFAULT 1,
        Formula_Offset FLOAT8 DEFAULT 0,
        Minimum FLOAT8 DEFAULT 0,
        Maximum FLOAT8 DEFAULT 0,
        Unit VARCHAR(255),
        "Comment" VARCHAR(255),
        PRIMARY KEY(RID)
    );
''', '''
    CREATE TABLE IF NOT EXISTS Attribute_Definition (
        RID INTEGER NOT NULL DEFAULT 0,
        Name VARCHAR(255) NOT NULL,
        Objecttype INTEGER NOT NULL DEFAULT 0,
        Valuetype INTEGER NOT NULL DEFAULT 0,
        Minimum FLOAT8 DEFAULT 0,
        Maximum FLOAT8 DEFAULT 0,
        Enumvalues TEXT,
        Default_Number FLOAT8 DEFAULT 0,
        Default_String VARCHAR(255),
        Column_Index INTEGER NOT NULL DEFAULT 0,
        "Comment" TEXT,
        PRIMARY KEY(RID)
    );
''', '''
    CREATE TABLE IF NOT EXISTS Attribute_Value (
        Object_ID INTEGER NOT NULL DEFAULT 0,
        Attribute_Definition INTEGER NOT NULL DEFAULT 0,
        Num_Value FLOAT8 DEFAULT 0,
        String_Value TEXT,
        PRIMARY KEY(Object_ID,Attribute_Definition),
        FOREIGN KEY(Attribute_Definition) REFERENCES Attribute_Definition(RID)
    );
''', '''
    CREATE TABLE IF NOT EXISTS AttributeRel_Value (
        Object_ID INTEGER NOT NULL DEFAULT 0,
        Attribute_Definition INTEGER NOT NULL DEFAULT 0,
        Num_Value FLOAT8 DEFAULT 0,
        String_Value TEXT,
        Opt_Object_ID_1 INTEGER DEFAULT 0,
        Opt_Object_ID_2 INTEGER DEFAULT 0,
        BLOB_Value BLOB,
        PRIMARY KEY(Object_ID,Attribute_Definition,Opt_Object_ID_1,Opt_Object_ID_2),
        FOREIGN KEY(Attribute_Definition) REFERENCES Attribute_Definition(RID)
    );
''', '''
    CREATE TABLE IF NOT EXISTS VndbMeta (
        Schema_Version INTEGER,
        Created TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
''', '''
    CREATE TABLE IF NOT EXISTS ECU (
        RID INTEGER NOT NULL DEFAULT 0,
        Name VARCHAR(255),
        "Comment" VARCHAR(255),
        PRIMARY KEY(RID)
    );
''', '''
    CREATE TABLE IF NOT EXISTS EnvVar (
        RID INTEGER NOT NULL DEFAULT 0,
        Name VARCHAR(255) NOT NULL,
        Type INTEGER NOT NULL DEFAULT 0,
        Unit VARCHAR(255),
        Minimum FLOAT8 DEFAULT 0,
        Maximum FLOAT8 DEFAULT 0,
        Startup_Value FLOAT8 DEFAULT 0,
        Size INTEGER DEFAULT 0,
        "Access" INTEGER DEFAULT 0,
        "Comment" VARCHAR(255),
        PRIMARY KEY(RID)
    );
''', '''
    CREATE TABLE IF NOT EXISTS ECU_EnvVar (
        ECU INTEGER NOT NULL DEFAULT 0,
        EnvVar INTEGER NOT NULL DEFAULT 0,
        PRIMARY KEY(ECU,EnvVar),
        FOREIGN KEY(ECU) REFERENCES ECU(RID),
        FOREIGN KEY(EnvVar) REFERENCES EnvVar(RID)
    );
''', '''
    CREATE TABLE IF NOT EXISTS ECU_Node (
        ECU INTEGER NOT NULL DEFAULT 0,
        Node INTEGER NOT NULL DEFAULT 0,
        PRIMARY KEY(ECU,Node),
        FOREIGN KEY(ECU) REFERENCES ECU(RID),
        FOREIGN KEY(Node) REFERENCES Node(RID)
    );
''', '''
    CREATE TABLE IF NOT EXISTS Gateway_Signal (
        RID INTEGER NOT NULL DEFAULT 0,
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
        PRIMARY KEY(RID)
    );
''', '''
    CREATE TABLE IF NOT EXISTS Node_Group (
        RID INTEGER NOT NULL DEFAULT 0,
        Name VARCHAR(255) NOT NULL,
        Node_Object_Type INTEGER NOT NULL DEFAULT 0,
        Node_Group_Type INTEGER NOT NULL DEFAULT 0,
        "Comment" VARCHAR(255),
        PRIMARY KEY(RID)
    );
''', '''
    CREATE TABLE IF NOT EXISTS Node_Group_Object (
        Parent_Type INTEGER NOT NULL DEFAULT 0,
        Parent_RID INTEGER NOT NULL DEFAULT 0,
        Object_Type INTEGER NOT NULL DEFAULT 0,
        Object_RID INTEGER NOT NULL DEFAULT 0,
        Object_RID_2 INTEGER NOT NULL DEFAULT 0,
        Opt_Object_Ref_1 INTEGER DEFAULT 0,
        Opt_Object_Ref_2 INTEGER DEFAULT 0,
        Opt_Object_Value INTEGER DEFAULT 0,
        PRIMARY KEY(Parent_Type,Parent_RID,Object_Type,Object_RID,Object_RID_2)
    );
''', '''
    CREATE TABLE IF NOT EXISTS Message_Signal (
        Message INTEGER NOT NULL DEFAULT 0,
        Signal INTEGER NOT NULL DEFAULT 0,
        "Offset" INTEGER NOT NULL DEFAULT 0,
        Multiplexor_Signal SMALLINT DEFAULT 0,
        Multiplex_Dependent SMALLINT DEFAULT 0,
        Multiplexor_Value INTEGER,
        PRIMARY KEY(Message,Signal),
        FOREIGN KEY(Message) REFERENCES Message(RID),
        FOREIGN KEY(Signal) REFERENCES Signal(RID)
    );
''', '''
    CREATE TABLE IF NOT EXISTS Network (
        RID INTEGER NOT NULL DEFAULT 0,
        Name VARCHAR(255) NOT NULL,
        "Comment" VARCHAR(255),
        Protocol INTEGER NOT NULL DEFAULT 0,
        Baudrate INTEGER DEFAULT 0,
        PRIMARY KEY(RID)
    );
''', '''
    CREATE TABLE IF NOT EXISTS Network_Node (
        Network INTEGER NOT NULL DEFAULT 0,
        Node INTEGER NOT NULL DEFAULT 0,
        PRIMARY KEY(Network,Node),
        FOREIGN KEY(Network) REFERENCES Network(RID),
        FOREIGN KEY(Node) REFERENCES Node(RID)
    );
''', '''
    CREATE TABLE IF NOT EXISTS Node_RxSig (
        Node INTEGER NOT NULL DEFAULT 0,
        Signal INTEGER NOT NULL DEFAULT 0,
        PRIMARY KEY(Node,Signal),
        FOREIGN KEY(Node) REFERENCES Node(RID),
        FOREIGN KEY(Signal) REFERENCES Signal(RID)
    );
''', '''
    CREATE TABLE IF NOT EXISTS Node_RxSignal (
        Node INTEGER NOT NULL DEFAULT 0,
        Message INTEGER NOT NULL DEFAULT 0,
        Signal INTEGER NOT NULL DEFAULT 0,
        PRIMARY KEY(Node,Message,Signal),
        FOREIGN KEY(Message) REFERENCES Message(RID),
        FOREIGN KEY(Node) REFERENCES Node(RID),
        FOREIGN KEY(Signal) REFERENCES Signal(RID)
    );
''', '''
    CREATE TABLE IF NOT EXISTS Node_TxMessage (
        Node INTEGER NOT NULL DEFAULT 0,
        Message INTEGER NOT NULL DEFAULT 0,
        PRIMARY KEY(Node,Message),
        FOREIGN KEY(Message) REFERENCES Message(RID),
        FOREIGN KEY(Node) REFERENCES Node(RID)
    );
''', '''
    CREATE TABLE IF NOT EXISTS Node_TxSig (
        Node INTEGER NOT NULL DEFAULT 0,
        Signal INTEGER NOT NULL DEFAULT 0,
        PRIMARY KEY(Node,Signal),
        FOREIGN KEY(Node) REFERENCES Node(RID),
        FOREIGN KEY(Signal) REFERENCES Signal(RID)
    );
''', '''
    CREATE TABLE IF NOT EXISTS Object_Valuetable (
        Object_Type INTEGER NOT NULL DEFAULT 0,
        Object_RID INTEGER NOT NULL DEFAULT 0,
        Valuetable INTEGER NOT NULL DEFAULT 0,
        PRIMARY KEY(Object_Type,Object_RID),
        FOREIGN KEY(Valuetable) REFERENCES Valuetable(RID)
    );
''', '''
    CREATE TABLE IF NOT EXISTS Value_Description (
        Valuetable INTEGER NOT NULL DEFAULT 0,
        Value FLOAT8 NOT NULL DEFAULT 0,
        Value_Description VARCHAR(255) NOT NULL,
        PRIMARY KEY(Valuetable,Value),
        FOREIGN KEY(Valuetable) REFERENCES Valuetable(RID)
    );
''', '''
    CREATE TABLE IF NOT EXISTS Valuetable (
        RID INTEGER NOT NULL DEFAULT 0,
        Name VARCHAR(255) NOT NULL,
        "Comment" VARCHAR(255),
        PRIMARY KEY(RID)
    );
''', '''
    CREATE TABLE IF NOT EXISTS Vehicle (
        RID INTEGER NOT NULL DEFAULT 0,
        Name VARCHAR(255) NOT NULL,
        "Comment" VARCHAR(255),
        PRIMARY KEY(RID)
    );
''', '''
    CREATE TABLE IF NOT EXISTS Vehicle_ECU (
        Vehicle INTEGER NOT NULL DEFAULT 0,
        ECU INTEGER NOT NULL DEFAULT 0,
        PRIMARY KEY(Vehicle,ECU),
        FOREIGN KEY(ECU) REFERENCES ECU(RID),
        FOREIGN KEY(Vehicle) REFERENCES Vehicle(RID)
    );
''', '''
    CREATE TABLE IF NOT EXISTS Vehicle_Network (
        Vehicle INTEGER NOT NULL DEFAULT 0,
        Network INTEGER NOT NULL DEFAULT 0,
        PRIMARY KEY(Vehicle,Network),
        FOREIGN KEY(Network) REFERENCES Network(RID),
        FOREIGN KEY(Vehicle) REFERENCES Vehicle(RID)
    );
''', '''
    CREATE TABLE IF NOT EXISTS Versioninfo (
        Obj_Type INTEGER NOT NULL DEFAULT 0,
        Obj_RID INTEGER NOT NULL DEFAULT 0,
        Version_Number INTEGER NOT NULL DEFAULT 0,
        Is_Modified BOOLEAN NOT NULL,
        PRIMARY KEY(Obj_Type,Obj_RID)
    );
''', '''
    CREATE VIEW IF NOT EXISTS schema AS SELECT * FROM sqlite_master;
''', '''
    CREATE TABLE IF NOT EXISTS comments(
        rid INTEGER NOT NULL DEFAULT 0,
        type CHAR(16),
        k0 CHAR(32),
        k1 CHAR(32),
        comment BLOB,
        PRIMARY KEY(rid)
    );
''', '''
    CREATE TEMPORARY TABLE IF NOT EXISTS EnvironmentVariablesData(
        name CHAR(256) NOT NULL,
        value INT NOT NULL,
        PRIMARY KEY(name)
    );
''','''
    CREATE TABLE IF NOT EXISTS EnvVar_AccessNode (
        EnvVar INTEGER NOT NULL DEFAULT 0,
        Node INTEGER NOT NULL DEFAULT 0,
        PRIMARY KEY(EnvVar, Node),
        FOREIGN KEY(EnvVar) REFERENCES EnvVar(RID),
        FOREIGN KEY(Node) REFERENCES Node(RID)
    );
''', )

DEFAULTS = (
    "INSERT OR REPLACE INTO Node(RID, Name, Comment) VALUES(0, 'Vector__XXX', 'Dummy node for non-existent senders/receivers.')",
)

TRIGGER = (
"""
""",
)

