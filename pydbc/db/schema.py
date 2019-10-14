#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Database schema.
"""

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

INDICES = (
    "CREATE UNIQUE INDEX IF NOT EXISTS Node_Name ON Node(Name)",
    "CREATE UNIQUE INDEX IF NOT EXISTS Attribute_Definition_Name ON Attribute_Definition(Name)",
    "CREATE INDEX IF NOT EXISTS Signal_Name ON Signal(Name)",
    "CREATE UNIQUE INDEX IF NOT EXISTS Message_Name ON Message(Name)",
    "CREATE UNIQUE INDEX IF NOT EXISTS EnvVar_Name ON EnvVar(Name)",
    "CREATE UNIQUE INDEX IF NOT EXISTS ECU_Name ON ECU(Name)",
    "CREATE UNIQUE INDEX IF NOT EXISTS Node_Group_Name ON Node_Group(Name)",
    "CREATE UNIQUE INDEX IF NOT EXISTS Network_Name ON Network(Name)",
    "CREATE INDEX IF NOT EXISTS Valuetable_Name ON Valuetable(Name)",
    "CREATE UNIQUE INDEX IF NOT EXISTS Vehicle_Name ON Vehicle(Name)",

)

TABLES = (
    "VndbMeta",
    "Message_Signal",
    "ECU_Node",
    "Network_Node",
    "Node_RxSig",
    "Node_RxSignal",
    "Node_TxMessage",
    "Node_TxSig",
    "Message",
    "Signal_Group_Signal",
    "Signal_Group",
    "Signal",
    "Attribute_Value",
    "AttributeRel_Value",
    "Attribute_Definition",
    "linAttribute_Value",
    "linAttribute_Definition",
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
    "Category_Value",
    "Category_Definition",
    "Dbc_Version",
    "Vndb_Protocol",
    "Vndb_Migrations",
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
        "Comment" VARCHAR(255) DEFAULT NULL,
        PRIMARY KEY(RID),
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
        FOREIGN KEY(Attribute_Definition) REFERENCES Attribute_Definition(RID) ON UPDATE CASCADE ON DELETE RESTRICT
    );
''', '''
    CREATE TABLE IF NOT EXISTS linAttribute_Definition (
        RID INTEGER NOT NULL DEFAULT 0,
        Name VARCHAR(255) NOT NULL,
        Objecttype INTEGER NOT NULL DEFAULT 0,
        Valuetype INTEGER NOT NULL DEFAULT 0,
        Minimum FLOAT8 DEFAULT 0,
        Maximum FLOAT8 DEFAULT 0,
        Enumvalues TEXT,
        Default_Number FLOAT8 DEFAULT 0,
        Default_String VARCHAR(255),
        "Comment" TEXT,
        PRIMARY KEY(RID)
    );
''', '''
    CREATE TABLE IF NOT EXISTS linAttribute_Value (
        Object_ID INTEGER NOT NULL DEFAULT 0,
        Attribute_Definition INTEGER NOT NULL DEFAULT 0,
        Num_Value FLOAT8 DEFAULT 0,
        String_Value TEXT,
        PRIMARY KEY(Object_ID,Attribute_Definition),
        FOREIGN KEY(Attribute_Definition) REFERENCES linAttribute_Definition(RID) ON UPDATE CASCADE ON DELETE RESTRICT
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
        FOREIGN KEY(Attribute_Definition) REFERENCES Attribute_Definition(RID) ON UPDATE CASCADE ON DELETE RESTRICT
    );
''', '''
    CREATE TABLE IF NOT EXISTS VndbMeta (
        RID INTEGER NOT NULL DEFAULT 0,
        Schema_Version INTEGER,
        Vndb_Type INTEGER NOT NULL DEFAULT 0,
        Created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY(RID)
    );
''', '''
    CREATE TABLE IF NOT EXISTS Vndb_Migrations (
        RID INTEGER NOT NULL,
        App varchar(255) NOT NULL,
        Name varchar(255) NOT NULL,
        Applied TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY(RID)
    );
''', '''
    CREATE TABLE IF NOT EXISTS Vndb_Protocol (
        Network INTEGER NOT NULL DEFAULT 0,
        Name varchar(255) NOT NULL,
        Specific varchar(255) NOT NULL,
        PRIMARY KEY(Network),
        FOREIGN KEY(Network) REFERENCES Network(RID) ON UPDATE CASCADE ON DELETE RESTRICT
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
        FOREIGN KEY(ECU) REFERENCES ECU(RID) ON UPDATE CASCADE ON DELETE RESTRICT,
        FOREIGN KEY(EnvVar) REFERENCES EnvVar(RID)ON UPDATE CASCADE ON DELETE RESTRICT
    );
''', '''
    CREATE TABLE IF NOT EXISTS ECU_Node (
        ECU INTEGER NOT NULL DEFAULT 0,
        Node INTEGER NOT NULL DEFAULT 0,
        PRIMARY KEY(ECU,Node),
        FOREIGN KEY(ECU) REFERENCES ECU(RID) ON UPDATE CASCADE ON DELETE RESTRICT,
        FOREIGN KEY(Node) REFERENCES Node(RID) ON UPDATE CASCADE ON DELETE RESTRICT
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
        FOREIGN KEY(Message) REFERENCES Message(RID) ON UPDATE CASCADE ON DELETE CASCADE,
        FOREIGN KEY(Signal) REFERENCES Signal(RID) ON UPDATE CASCADE ON DELETE CASCADE
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
        FOREIGN KEY(Network) REFERENCES Network(RID) ON UPDATE CASCADE ON DELETE RESTRICT,
        FOREIGN KEY(Node) REFERENCES Node(RID) ON UPDATE CASCADE ON DELETE RESTRICT
    );
''', '''
    CREATE TABLE IF NOT EXISTS Node_RxSig (
        Node INTEGER NOT NULL DEFAULT 0,
        Signal INTEGER NOT NULL DEFAULT 0,
        PRIMARY KEY(Node,Signal),
        FOREIGN KEY(Node) REFERENCES Node(RID) ON UPDATE CASCADE ON DELETE RESTRICT,
        FOREIGN KEY(Signal) REFERENCES Signal(RID) ON UPDATE CASCADE ON DELETE RESTRICT
    );
''', '''
    CREATE TABLE IF NOT EXISTS Node_RxSignal (
        Node INTEGER NOT NULL DEFAULT 0,
        Message INTEGER NOT NULL DEFAULT 0,
        Signal INTEGER NOT NULL DEFAULT 0,
        PRIMARY KEY(Node,Message,Signal),
        FOREIGN KEY(Message) REFERENCES Message(RID) ON UPDATE CASCADE ON DELETE CASCADE,
        FOREIGN KEY(Node) REFERENCES Node(RID) ON UPDATE CASCADE ON DELETE CASCADE,
        FOREIGN KEY(Signal) REFERENCES Signal(RID) ON UPDATE CASCADE ON DELETE CASCADE
    );
''', '''
    CREATE TABLE IF NOT EXISTS Node_TxMessage (
        Node INTEGER NOT NULL DEFAULT 0,
        Message INTEGER NOT NULL DEFAULT 0,
        PRIMARY KEY(Node,Message),
        FOREIGN KEY(Message) REFERENCES Message(RID) ON UPDATE CASCADE ON DELETE CASCADE,
        FOREIGN KEY(Node) REFERENCES Node(RID) ON UPDATE CASCADE ON DELETE CASCADE
    );
''', '''
    CREATE TABLE IF NOT EXISTS Node_TxSig (
        Node INTEGER NOT NULL DEFAULT 0,
        Signal INTEGER NOT NULL DEFAULT 0,
        PRIMARY KEY(Node,Signal),
        FOREIGN KEY(Node) REFERENCES Node(RID) ON UPDATE CASCADE ON DELETE CASCADE,
        FOREIGN KEY(Signal) REFERENCES Signal(RID) ON UPDATE CASCADE ON DELETE CASCADE
    );
''', '''
    CREATE TABLE IF NOT EXISTS Signal_Group(
        RID INTEGER NOT NULL DEFAULT 0,
        Name VARCHAR(255) NOT NULL,
        Value INTEGER NOT NULL DEFAULT 0,
        Message INTEGER NOT NULL DEFAULT 0,
        PRIMARY KEY(RID),
        UNIQUE(Message, Name),
        FOREIGN KEY(Message) REFERENCES Message(RID) ON UPDATE CASCADE ON DELETE CASCADE
    );
''', '''
    CREATE TABLE IF NOT EXISTS Signal_Group_Signal(
        Signal_Group INTEGER NOT NULL DEFAULT 0,
        Message INTEGER NOT NULL DEFAULT 0,
        Signal INTEGER NOT NULL DEFAULT 0,
        PRIMARY KEY(Signal_Group, Message, Signal),
        FOREIGN KEY(Signal_Group) REFERENCES Signal_Group(RID) ON UPDATE CASCADE ON DELETE CASCADE,
        FOREIGN KEY(Message) REFERENCES Message(RID) ON UPDATE CASCADE ON DELETE CASCADE,
        FOREIGN KEY(Signal) REFERENCES Signal(RID) ON UPDATE CASCADE ON DELETE CASCADE
    );
''', '''
    CREATE TABLE IF NOT EXISTS Object_Valuetable (
        Object_Type INTEGER NOT NULL DEFAULT 0,
        Object_RID INTEGER NOT NULL DEFAULT 0,
        Valuetable INTEGER NOT NULL DEFAULT 0,
        PRIMARY KEY(Object_Type, Object_RID),
        FOREIGN KEY(Valuetable) REFERENCES Valuetable(RID) ON UPDATE CASCADE ON DELETE CASCADE
    );
''', '''
    CREATE TABLE IF NOT EXISTS Value_Description (
        Valuetable INTEGER NOT NULL DEFAULT 0,
        Value FLOAT8 NOT NULL DEFAULT 0,
        Value_Description VARCHAR(255) NOT NULL,
        PRIMARY KEY(Valuetable,Value),
        FOREIGN KEY(Valuetable) REFERENCES Valuetable(RID) ON UPDATE CASCADE ON DELETE CASCADE
    );
''', '''
    CREATE TABLE IF NOT EXISTS Valuetable(
        RID INTEGER NOT NULL DEFAULT 0,
        Name VARCHAR(255),
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
        FOREIGN KEY(ECU) REFERENCES ECU(RID) ON UPDATE CASCADE ON DELETE RESTRICT,
        FOREIGN KEY(Vehicle) REFERENCES Vehicle(RID) ON UPDATE CASCADE ON DELETE RESTRICT
    );
''', '''
    CREATE TABLE IF NOT EXISTS Vehicle_Network (
        Vehicle INTEGER NOT NULL DEFAULT 0,
        Network INTEGER NOT NULL DEFAULT 0,
        PRIMARY KEY(Vehicle,Network),
        FOREIGN KEY(Network) REFERENCES Network(RID) ON UPDATE CASCADE ON DELETE RESTRICT,
        FOREIGN KEY(Vehicle) REFERENCES Vehicle(RID) ON UPDATE CASCADE ON DELETE RESTRICT
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
    CREATE TABLE IF NOT EXISTS Category_Definition (
        RID INTEGER NOT NULL DEFAULT 0,
        Name VARCHAR(255) NOT NULL,
        Key INTEGER NOT NULL DEFAULT 0,
        Level INTEGER NOT NULL DEFAULT 0,
        UNIQUE(Key),
        PRIMARY KEY(RID)
    );
''', '''
    CREATE TABLE IF NOT EXISTS Category_Value (
        Object_ID INTEGER NOT NULL DEFAULT 0,
        Category_Definition INTEGER NOT NULL DEFAULT 0,
        Objecttype INTEGER NOT NULL DEFAULT 0,
        PRIMARY KEY(Object_ID, Objecttype),
        FOREIGN KEY(Category_Definition) REFERENCES Category_Definition(Key) ON UPDATE CASCADE ON DELETE RESTRICT
    );
''', '''
    CREATE TABLE IF NOT EXISTS Dbc_Version (
        RID INTEGER NOT NULL DEFAULT 0,
        Version_String VARCHAR(255) DEFAULT '',
        Network INTEGER NOT NULL DEFAULT 0,
        UNIQUE(Network),
        PRIMARY KEY(RID)
    );
''', '''
    CREATE VIEW IF NOT EXISTS schema AS SELECT * FROM sqlite_master;
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
        FOREIGN KEY(EnvVar) REFERENCES EnvVar(RID) ON UPDATE CASCADE ON DELETE RESTRICT,
        FOREIGN KEY(Node) REFERENCES Node(RID) ON UPDATE CASCADE ON DELETE RESTRICT
    );
''', )

DEFAULTS = (
    "INSERT OR REPLACE INTO Node(RID, Name, Comment) VALUES(0, 'Vector__XXX', 'Dummy node for non-existent senders/receivers.')",
)

TRIGGER = (
"""
    CREATE TRIGGER IF NOT EXISTS Insert_Message AFTER INSERT ON Message
    BEGIN
        INSERT INTO Node_TxMessage(Message, Node) VALUES (new.RID, new.Sender);
    END;
""",
"""
    CREATE TRIGGER IF NOT EXISTS Insert_Node_TxMessage_0 AFTER INSERT ON Node_TxMessage
    WHEN new.Node <> 0
    BEGIN
        DELETE FROM Node_TxMessage WHERE Message = new.Message AND Node = 0;
    END;
""",
"""
    CREATE TRIGGER IF NOT EXISTS Insert_Node_TxMessage_1 AFTER INSERT ON Node_TxMessage
    WHEN new.Node = 0 AND (select exists (select * from Node_TxMessage where Message = new.Message AND Node <> 0)) = 1
    BEGIN
        SELECT RAISE(ABORT, 'Dummy sender invalid in present state.');
    END;
""",
)

##
##> CREATE TRIGGER <trigger-name> AFTER INSERT on <table-name> WHEN EXISTS
##> (select * from <some-table>)
##>
##> BEGIN
##>
##>                RAISE(ROLLBACK);
##>
##> END
##
##create trigger <trigger-name> after insert on <table-name>
##        begin
##                select raise(rollback) when exists (select * from <some-table>);
##        end
##
