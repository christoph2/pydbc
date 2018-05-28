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

    "CREATE INDEX Cdb_Signal_Name ON Cdb_Signal(Name)",
)

TABLES = (
    "Cdb_Message_Signal",
    "Cdb_ECU_Node",
    "Cdb_Network_Node",
    "Cdb_Node_RxSig",
    "Cdb_Node_RxSignal",
    "Cdb_Node_TxMessage",
    "Cdb_Node_TxSig",
    "Cdb_Node",
    "Cdb_Message",
    "Cdb_Signal",
    "Cdb_Attribute_Value",
    "Cdb_AttributeRel_Value",
    "Cdb_Attribute_Definition",
    "Cdb_DB_Info",
    "Cdb_ECU_EnvVar",
    "Cdb_ECU",
    "Cdb_EnvVar",
    "Cdb_Gateway_Signal",
    "Cdb_Group",
    "Cdb_Group_Object",
    "Cdb_Network",
    "Cdb_Object_Valuetable",
    "Cdb_Value_Description",
    "Cdb_Valuetable",
    "Cdb_Vehicle",
    "Cdb_Vehicle_Network",
    "Cdb_Vehicle_ECU",
    "Cdb_Versioninfo",
    "comments",
    "EnvironmentVariablesData",
)

VIEWS = (
    "schema",
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
        Enumvalues TEXT,
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

TRIGGER = (
"""
""",
)
