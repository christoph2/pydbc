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


from pydbc.logger import Logger
from pydbc.types import AttributeType, ValueType

class Loader(object):

    def __init__(self, db):
        self.db = db
        self.logger = Logger('db.loader')

    def insertValues(self, tree):
        cur = self.db.getCursor()
        self.db.beginTransaction()

        self.insertEnvironmentVariablesData(cur, tree['environmentVariablesData'])
        self.insertComments(cur, tree['comments'])
        self.insertValueTables(cur, tree['valueTables'])
        self.insertNodes(cur, tree['nodes'])
        self.insertMessages(cur, tree['messages'])
        self.insertEnvironmentVariables(cur, tree['environmentVariables'])

        self.insertValueDescriptions(cur, tree['valueDescriptions'])

        defaults = tree['attributeDefaults']
        self.insertAttributeDefinitions(cur, tree['attributeDefinitions'], defaults)
        self.db.commitTransaction()

    def insertValueTables(self, cur, tables):
        for table in tables:
            name = table['name']
            description = table['description']
            self.db.insertStatement(cur, "Valuetable", "Name", name)
            res = cur.execute("SELECT RID FROM Valuetable WHERE Name = ?", [name]).fetchall()
            rid = res[0][0]
            self.insertValueDescription(cur, rid, description)

    def insertValueDescription(self, cur, rid, description):
        for desc, value in description:
            self.db.insertStatement(cur, "Value_Description", "Valuetable, Value, Value_Description", rid, value, desc)

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
            cmt = self.db.fetchComment('EV', name)
            dataSize = self.db.fetchEnvironmentVariablesData(name)
            self.db.insertStatement(cur, "EnvVar", "Name, Type, Unit, Minimum, Maximum, Access, Startup_Value, Comment, Size",
                name, varType, unit, minimum, maximum, accessType, initialValue, cmt, dataSize
            )
            evid = self.db.lastInsertedRowId(cur, "EnvVar")
            for node in accessNodes:
                nid = self.db.fetchNodeId(node)
                self.db.insertStatement(cur, "EnvVar_AccessNode", "EnvVar,Node", evid, nid)


    def insertValueDescriptions(self, cur, descriptions):
        for item in descriptions:
            tp = item['type']
            description = item['description']
            if tp == 'SG':
                messageID = item['messageID']
                name = item['signalName']
                otype = 0
                rid = cur.execute("""SELECT t1.RID FROM signal AS t1, Message_Signal AS t2 where
                    t1.RID = t2.signal AND t1.name = ? AND t2.message = (SELECT RID FROM message
                    WHERE message_id = ?)""", [name, messageID]
                ).fetchone()[0]
                #print("\tS-RID", messageID, rid, item, flush = True)
            elif tp == 'EV':
                name = item['envVarName']
                otype = 1
                rid = cur.execute("SELECT RID FROM EnvVar WHERE name = ?", [name]).fetchone()[0]
                print("\tE-RID", rid, item, flush = True)
            self.db.insertStatement(cur, "Valuetable", "Name", name)
            vtid = self.db.lastInsertedRowId(cur, "Valuetable")
            self.db.insertStatement(cur, "Object_Valuetable", "Object_Type, Object_RID, Valuetable", otype, rid, vtid)
            self.insertValueDescription(cur, vtid, description)
        print("-" * 80)


    def insertReceivers(self, cur, messageId, signalId, receiver):
        for rcv in receiver:
            nodeId = self.db.fetchNodeId(rcv)
            self.db.insertStatement(cur, "Node_RxSignal", "Message, Signal, Node", messageId, signalId, nodeId)

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
            self.db.insertStatement(cur, "comments", "type, k0, k1, comment", tp, k0, k1, text)

    def insertEnvironmentVariablesData(self, cur, data):
        for item in data:
            name = item['name']
            value = item['value']
            print(name, value)
            self.db.insertStatement(cur, "EnvironmentVariablesData", "name, value", name, value)

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
            self.db.insertStatement(cur, "Attribute_Definition", """Name, Objecttype, Valuetype, Minimum, Maximum, Enumvalues,
                Default_Number, Default_String""", name, objType, valueType, minimum, maximum, enumvalues, defaultNumber, defaultString
            )

        '''
        ''', '''
            CREATE TABLE Attribute_Value (
                Object_ID INTEGER NOT NULL DEFAULT 0,
                Attribute_Definition INTEGER NOT NULL DEFAULT 0,
                Num_Value FLOAT8 DEFAULT 0,
                String_Value TEXT,
                PRIMARY KEY(Object_ID,Attribute_Definition),
                FOREIGN KEY(Attribute_Definition) REFERENCES Attribute_Definition(RID)
            );
        ''', '''
            CREATE TABLE AttributeRel_Value (
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
        '''

    def insertNodes(self, cur, nodes):
        self.db.insertStatement(cur, "Node", "RID, Name", 0, "Vector__XXX")
        for node in nodes:
            cmt = self.db.fetchComment('BU', node)
            self.db.insertStatement(cur, "Node", "Name, Comment", node, cmt)

    def insertMessages(self, cur, messages):
        for msg in messages:
            name = msg['name']
            mid = msg['messageID']
            # 0xCFFFFFFF
            dlc = msg['dlc']
            signals = msg['signals']
            cmt = self.db.fetchComment('BO', mid)

            transmitter = msg['transmitter']
            tid = self.db.fetchNodeId(transmitter)

            self.db.insertStatement(cur, "Message", "Name, Message_ID, DLC, Comment, Sender", name, mid, dlc, cmt, tid)
            mrid = self.db.lastInsertedRowId(cur, "Message")
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
                cmt = self.db.fetchComment('SG', mid, name)
                self.db.insertStatement(cur, "Signal", """Name, Bitsize, Byteorder, Valuetype, Initialvalue, Formula_Factor, Formula_Offset,
                    Minimum, Maximum, Unit, Comment""",
                    name, signalSize, byteOrder, valueType, initialValue, factor, offset, minimum, maximum, unit, cmt
                )
                srid = self.db.lastInsertedRowId(cur, "Signal")
                self.db.insertStatement(cur, "Message_Signal", "Message, Signal, Offset, Multiplexor_Signal, Multiplex_Dependent, Multiplexor_Value",
                    mrid, srid, startBit, multiplexorSignal, multiplexDependent, multiplexorValue
                )
                self.insertReceivers(cur, mrid, srid, receiver)

