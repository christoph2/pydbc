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

from pydbc.logger import Logger
from pydbc.types import AttributeType, ValueType, CategoryType


class Comments:
    """This class contains the comments found in .dbc files.
    """
    def __init__(self):
        self.bu = {}
        self.bo = {}
        self.sg = {}
        self.ev = {}
        self.nw = None

##
##    def __del__(self):
##        from pprint import pprint
##        pprint(self.bu)
##        pprint(self.bo)
##        pprint(self.sg)
##        pprint(self.ev)
##

    def addNode(self, key, value):
        self.bu[key] = value

    def addMessage(self, key, value):
        self.bo[key] = value

    def addSignal(self, key, value):
        self.sg[key] = value

    def addEnvVar(self, key, value):
        self.ev[key] = value

    def addNetwork(self, value):
        self.nw = value

    def node(self, key):
        return self.bu.get(key)

    def message(self, key):
        return self.bo.get(key)

    def signal(self, key):
        return self.sg.get(key)

    def envVar(self, key):
        return self.ev.get(key)

    def network(self):
        return self.nw


class Loader(object):

    def __init__(self, db, queryClass):
        self.db = db
        self.comments = Comments()
        self.queries = queryClass(db)
        self.logger = Logger(__name__)

    def insertValues(self, tree):
        cur = self.db.getCursor()
        self.db.beginTransaction()
        self.insertVersion(cur, tree['version'])
        self.insertEnvironmentVariablesData(cur, tree['environmentVariablesData'])
        self.insertComments(cur, tree['comments'])
        self.insertValueTables(cur, tree['valueTables'])
        self.insertNetwork(cur)
        self.insertNodes(cur, tree['nodes'])
        valueTypes = self.processExtendedSignalValueTypes(cur, tree['signalExtendedValueTypeList'])
        self.insertMessages(cur, tree['messages'], valueTypes)
        self.insertEnvironmentVariables(cur, tree['environmentVariables'])
        self.insertMessageTransmitters(cur, tree['messageTransmitters'])
        self.insertValueDescriptions(cur, tree['valueDescriptions'])
        defaults = tree['attributeDefaults']
        self.insertAttributeDefinitions(cur, tree['attributeDefinitions'], defaults)
        self.insertAttributes(cur, tree['attributeValues'])
        defaults = tree['relativeAttributeDefaults']

        self.insertRelativeAttributeDefinitions(cur, tree['relativeAttributeDefinitions'], defaults)
        self.insertCategoryDefinitions(cur, tree['categoryDefinitions'])
        self.insertCategoryValues(cur, tree['categories'])
        self.db.commitTransaction()

    def processExtendedSignalValueTypes(self, cur, valueTypes):
        keyFunc = lambda k: k['messageID']
        result = dict()
        valueTypes = sorted(valueTypes, key = keyFunc)
        for group in itertools.groupby(valueTypes, keyFunc):
            key, grouper = group
            result[key] = {}
            for item in grouper:
                result[key][item['signalName']] = item['valueType']
        return result

    def insertVersion(self, cur, version):
        network = 0 ## TODO: Real value!!!
        self.db.insertStatement(cur, "Dbc_Version", "Version_String, Network", version, network)

    def insertNetwork(self, cur):
        comment = self.comments.network()
        self.db.insertStatement(cur, "Network", "Name, Comment", self.db.name, comment)

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
            cmt = self.comments.envVar(name)
            dataSize = self.queries.fetchEnvironmentVariablesData(name)
            self.db.insertStatement(cur, "EnvVar", "Name, Type, Unit, Minimum, Maximum, Access, Startup_Value, Comment, Size",
                name, varType, unit, minimum, maximum, accessType, initialValue, cmt, dataSize
            )
            evid = cur.lastrowid
            for node in accessNodes:
                nid = self.queries.fetchNodeId(node)
                self.db.insertStatement(cur, "EnvVar_AccessNode", "EnvVar,Node", evid, nid)

    def getSignalByName(self, cur, messageID, name):
        return cur.execute("""SELECT t1.RID FROM signal AS t1, Message_Signal AS t2 where
            t1.RID = t2.signal AND t1.name = ? AND t2.message = (SELECT RID FROM message
            WHERE message_id = ?)""", [name, messageID]
        ).fetchone()[0]

    def insertValueDescriptions(self, cur, descriptions):
        for item in descriptions:
            tp = item['type']
            description = item['description']
            if tp == 'SG':
                messageID = item['messageID']
                name = item['signalName']
                otype = 0
                rid = self.getSignalByName(cur, messageID, name)
            elif tp == 'EV':
                name = item['envVarName']
                otype = 1
                rid = cur.execute("SELECT RID FROM EnvVar WHERE name = ?", [name]).fetchone()[0]
            self.db.insertStatement(cur, "Valuetable", "Name", name)
            vtid = cur.lastrowid
            self.db.insertStatement(cur, "Object_Valuetable", "Object_Type, Object_RID, Valuetable", otype, rid, vtid)
            self.insertValueDescription(cur, vtid, description)

    def insertReceivers(self, cur, messageId, signalId, receiver):
        SignalReceivers = set()
        for rcv in receiver:
            nodeId = self.queries.fetchNodeId(rcv)
            if not (messageId, signalId, nodeId) in SignalReceivers:
                self.db.insertStatement(cur, "Node_RxSignal", "Message, Signal, Node", messageId, signalId, nodeId)
            SignalReceivers.add((messageId, signalId, nodeId))

    def insertComments(self, cur, comments):
        for comment in comments:
            tp = comment['type']
            text = comment['comment']
            key = comment['key']
            if tp == 'BU':
                self.comments.addNode(key, text)
            elif tp == 'BO':
                self.comments.addMessage(key, text)
            elif tp == 'SG':
                self.comments.addSignal(key, text)
            elif tp == 'EV':
                self.comments.addEnvVar(key,text)
            else:   # NW !?
                self.comments.addNetwork(text)

    def insertEnvironmentVariablesData(self, cur, data):
        for item in data:
            name = item['name']
            value = item['value']
            #print(name, value)
            self.db.insertStatement(cur, "EnvironmentVariablesData", "name, value", name, value)

    def insertCategoryDefinitions(self, cur, catagories):
        for category in catagories:
            self.db.insertStatement(cur, "Category_Definition", "name, key, level",
                category['name'], category['category'], category['value']
            )

    def insertCategoryValues(self, cur, catagories):
        for category in catagories:
            attrType = category['type']
            catId = category['category']
            if attrType == 'BU':
                nodeName = category['nodeName']
                objType = CategoryType.NODE
                rid = self.queries.fetchNodeId(nodeName)
            elif attrType == 'BO':
                objType = CategoryType.MESSAGE
                messageID = category['messageID']
                rid = self.queries.fetchMessageIdById(messageID)
            elif attrType == 'EV':
                envVarname = category['envVarname']
                objType = CategoryType.ENV_VAR
                rid = self.queries.fetchEnvVarId(envVarname)
            self.db.insertStatement(cur, "Category_Value", "Object_ID,Category_Definition,Objecttype", rid, catId, objType)


    def insertRelativeAttributeDefinitions(self, cur, attrs, defaults):
        print("C-A-D: {}\n\n{}".format(attrs, defaults))


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
                objType = AttributeType.NETWORK
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

    def getAttributeType(self, value):
        ATS = {
            "NETWORK": AttributeType.NETWORK,
            "BU": AttributeType.NODE,
            "BO": AttributeType.MESSAGE,
            "SG": AttributeType.SIGNAL,
            "EV": AttributeType.ENV_VAR
        }
        return ATS.get(value)

    def insertAttributes(self, cur, attrs):
        for attr in attrs:
            stringValue = None
            numValue = None
            value = attr['value']
            if isinstance(value, str):
                stringValue = value
            else:
                numValue = value
            aid = self.queries.fetchAttributeId(attr['name'])
            attrType = self.getAttributeType(attr['type'])
            if attrType == AttributeType.MESSAGE:
                rid = self.queries.fetchMessageIdById(attr['messageID'])
            elif attrType == AttributeType.SIGNAL:
               rid = self.getSignalByName(cur, attr['messageID'], attr['signalName'])
            elif attrType == AttributeType.NODE:
                rid = self.queries.fetchNodeId(attr['nodeName'])
            elif attrType == AttributeType.ENV_VAR:
                rid = self.queries.fetchEnvVarId(attr['envVarname'])
            elif attrType == AttributeType.NETWORK:
                rid = 0
            else:
                rid = 0
            self.db.insertStatement(cur, "Attribute_Value", "Object_ID, Attribute_Definition, Num_Value, String_Value",
                rid, aid, numValue, stringValue
            )

    def insertNodes(self, cur, nodes):
        nodeSet = set()
        for node in nodes:
            cmt = self.comments.node(node)
            if not node in nodeSet:
                self.db.insertStatement(cur, "Node", "Name, Comment", node, cmt)
            nodeSet.add(node)

    def insertMessageTransmitters(self, cur, transmitters):
        for transmitter in transmitters:
            mid = self.queries.fetchMessageIdById(transmitter['messageID'])
            for name in transmitter['transmitters']:
                nid = self.queries.fetchNodeId(name)
                self.db.replaceStatement(cur, "Node_TxMessage", "Node, Message", nid, mid)

    def insertMessages(self, cur, messages, valueTypes):
        for msg in messages:
            name = msg['name']
            mid = msg['messageID']
            dlc = msg['dlc']
            signals = msg['signals']
            cmt = self.comments.message(mid)

            transmitter = msg['transmitter']
            tid = self.queries.fetchNodeId(transmitter)
            valueTypesForMessage = valueTypes.get(mid, {})
            mrid = self.db.insertStatement(cur, "Message", "Name, Message_ID, DLC, Comment, Sender", name, mid, dlc, cmt, tid)
            #if tid != 0:
            #    self.db.insertStatement(cur, "Node_TxMessage", "Node, Message", tid, mrid)
            for signal in signals:
                name = signal['name']
                startBit = signal['startBit']
                signalSize = signal['signalSize']
                byteOrder = signal['byteOrder']
                sign = signal['sign']
                factor = signal['factor']
                offset = signal['offset']
                minimum = signal['minimum']
                maximum = signal['maximum']
                unit = signal['unit']
                receiver = signal['receiver']
                valueTypeForSignal = valueTypesForMessage.get(name, None)
                valueType = valueTypeForSignal if valueTypeForSignal is not None else 0
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
                cmt = self.comments.signal((mid, name, ))
                self.db.insertStatement(cur, "Signal", """Name, Bitsize, Byteorder, Sign, Valuetype, Formula_Factor, Formula_Offset,
                    Minimum, Maximum, Unit, Comment""",
                    name, signalSize, byteOrder, sign, valueType, factor, offset, minimum, maximum, unit, cmt
                )
                srid = cur.lastrowid
                self.db.insertStatement(cur, "Message_Signal", "Message, Signal, Offset, Multiplexor_Signal, Multiplex_Dependent, Multiplexor_Value",
                    mrid, srid, startBit, multiplexorSignal, multiplexDependent, multiplexorValue
                )
                self.insertReceivers(cur, mrid, srid, receiver)

