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

from pydbc.types import AttributeType, ValueType, CategoryType
from .base import BaseLoader

from pydbc.db.model import (
    Dbc_Version, Message, Message_Signal, Network, Node, Signal, Value_Description, 
    Valuetable, EnvironmentVariablesData, EnvVar
)

"""
FIBEX elements              CANdb object type
---------------------------------------------
CLUSTER, CHANNEL            Network
ECU, CONTROLLER, CONNECTOR  Network Node
FRAME, FRAME-TRIGGERING     Message
SIGNAL, SIGNAL-INSTANCE     Message Signals

The following information has no equivalent description in CANdb:
- PDUs and Functions aren't used in CANdb.
- Controller  information  isn't  used  in  CANdb  databases.  This  information  may  be stored as node attributes.
- CAN  remote  frames  aren't  stored  in  CANdb  databases.  This  information  isn't generated during export and
  will be ignored during import.
"""

class Comments:
    """This class contains the comments found in .dbc files.
    """
    def __init__(self):
        self.bu = {}
        self.bo = {}
        self.sg = {}
        self.ev = {}
        self.nw = None

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


class DbcLoader(BaseLoader):

    def __init__(self, db, queryClass):
        super(DbcLoader, self).__init__(db, queryClass)
        self.comments = Comments()

    def _insertValues(self, tree):
        cur = None
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
        self.insertAttributeDefinitions(cur, tree['relativeAttributeDefinitions'], defaults)
        self.insertRelativeAttributes(cur, tree['relativeAttributeValues'])
        self.insertSignalGroups(cur, tree['signalGroups'])
        self.insertCategoryDefinitions(cur, tree['categoryDefinitions'])
        self.insertCategoryValues(cur, tree['categories'])

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
        vers = Dbc_Version(version_string = version, network = network)
        self.session.add(vers)
        res = self.session.query(Dbc_Version).all()
        print("Dbc_Version", res)

    def insertNetwork(self, cur):
        comment = self.comments.network()
        network = Network(name = self.db.dbname, comment = comment)
        self.session.add(network)

    def insertValueTables(self, cur, tables):
        for table in tables:
            name = table['name']
            description = table['description']
            vt = Valuetable(name = name)
            self.session.add(vt)
            self.insertValueDescription(vt.rid, description)

    def insertValueDescription(self, rid, description):
        for desc, value in description:
            vd = Value_Description(valuetable = rid, value = value, value_description = desc)
            self.session.add(vd)

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
            dataSize = self.session.query(EnvironmentVariablesData.value).filter(EnvironmentVariablesData.name == name).scalar()            
            envVar = EnvVar(name = name, type = varType, unit = unit, minimum = minimum, maximum = maximum,
                access = accessType, startup_value = initialValue, comment = cmt, size = dataSize)
            self.session.add(envVar)
            #print("ENV-VAR", envVar)
            #evid = cur.lastrowid
            for node in accessNodes:
                nn = self.session.query(Node).filter(Node.name == node).one()
                envVar.accessingNodes.append(nn)
            #print("AN_S", envVar.accessingNodes)
        self.session.commit()

    def get_signal_by_name(self, messageID, name):
        return self.session.query(Signal.rid).join(Message_Signal).join(Message).\
            filter(Message.message_id == messageID, Signal.name == name).scalar()
        #return cur.execute("""SELECT t1.RID FROM signal AS t1, Message_Signal AS t2 where
        #    t1.RID = t2.signal AND t1.name = ? AND t2.message = (SELECT RID FROM message
        #    WHERE message_id = ?)""", [name, messageID]
        #).fetchone()[0]

    def insertValueDescriptions(self, cur, descriptions):
        for item in descriptions:
            print("VD-ITEM", item)
            tp = item['type']
            description = item['description']
            if tp == 'SG':
                messageID = item['messageID']
                name = item['signalName']
                otype = 0
                rid = self.get_signal_by_name(messageID, name)
            elif tp == 'EV':
                name = item['envVarName']
                otype = 1
                rid = self.session.query(EnvVar.rid).filter(EnvVar.name == name).scalar()
            ###
            vt = Valuetable(name = name)
            self.session.add(vt)

            #self.db.insertStatement(cur, "Valuetable", "Name", name)
            #vtid = cur.lastrowid
            
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
            #self.db.insertStatement(cur, "EnvironmentVariablesData", "name, value", name, value)
            evd = EnvironmentVariablesData(name = name, value = value)
            self.session.add(evd)
            print(evd)

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
            elif attrType == 'BU_BO_REL_':
                objType = AttributeType.REL_NODE
            elif attrType == 'BU_SG_REL_':
                objType = AttributeType.REL_SIGNAL
            elif attrType == 'BU_EV_REL_':
                objType = AttributeType.REL_ENV_VAR
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
            "EV": AttributeType.ENV_VAR,
            "REL_NODE": AttributeType.REL_NODE,
            "REL_SIGNAL": AttributeType.REL_SIGNAL,
            "REL_ENV_VAR": AttributeType.REL_ENV_VAR,
        }
        return ATS.get(value)

    def insertAttributes(self, cur, attrs):
        for attr in attrs:
            stringValue = None
            numValue = None
            value = attr['attributeValue']
            if isinstance(value, str):
                stringValue = value
            else:
                numValue = value
            aid = self.queries.fetchAttributeId(attr['name'])
            attrType = self.getAttributeType(attr['attributeType'])
            if attrType == AttributeType.MESSAGE:
                rid = self.queries.fetchMessageIdById(attr['messageID'])
            elif attrType == AttributeType.SIGNAL:
               rid = self.get_signal_by_name(attr['messageID'], attr['signalName'])
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

    def insertRelativeAttributes(self, cur, attrs):
        for attr in attrs:
            attributeName = attr['attributeName']
            attributeValue = attr['attributeValue']
            attrributeType = self.getAttributeType(attr['attributeType'])
            aid = self.queries.fetchAttributeId(attr['attributeName'])
            nodeId = self.queries.fetchNodeId(attr['nodeName'])
            parent = attr['parent']
            optOid1 = nodeId
            optOid2 = None
            stringValue = None
            numValue = None
            value = attr['attributeValue']
            if isinstance(value, str):
                stringValue = value
            else:
                numValue = value
            if attrributeType == AttributeType.REL_SIGNAL:
                messageID = parent['messageID']
                optOid2 = messageID
                rid = self.get_signal_by_name(messageID, parent['signalName'])
            elif attrributeType == AttributeType.REL_ENV_VAR:
                evName = parent['evName']
                rid = self.queries.fetchEnvVarId(evName)
            elif attrributeType == AttributeType.REL_NODE:
                messageID = parent['messageID']
                optOid2 = messageID
                rid = self.queries.fetchMessageIdById(messageID)
            self.db.insertStatement(cur, "AttributeRel_Value",
                """Object_ID, Attribute_Definition, Num_Value, String_Value, Opt_Object_ID_1, Opt_Object_ID_2""",
                rid, aid, numValue, stringValue, optOid1, optOid2
            )

    def insertSignalGroups(self, cur, signalGroups):
        for group in signalGroups:
            messageID = group['messageID']
            gValue = group['gvalue']
            signalNames = group['signals']
            groupName = group['groupName']
            rid = self.queries.fetchMessageIdById(messageID)
            self.db.insertStatement(cur, "Signal_Group", "Name, Value, Message", groupName, gValue, rid)
            sgrid = cur.lastrowid
            for signalName in signalNames:
                mrid, srid =  self.queries.fetchMessageSignalByMessageIDandSignalName(messageID, signalName)
                self.db.insertStatement(cur, "Signal_Group_Signal", "Signal_Group, Message, Signal", sgrid, mrid, srid)

    def insertNodes(self, cur, nodes):
        nodeSet = set()
        for node in nodes:
            comment = self.comments.node(node)
            if not node in nodeSet:
                nn = Node(name = node, comment = comment)
                self.session.add(nn)
            nodeSet.add(node)
        #self.session.commit()

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
            tid = self.session.query(Node.rid).filter(Node.name == transmitter).scalar()
            valueTypesForMessage = valueTypes.get(mid, {})
            mm = Message(name = name, message_id = mid, dlc = dlc, comment = cmt, sender = tid)
            self.session.add(mm)
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
                
                ss = Signal(name = name, bitsize = signalSize, byteorder = byteOrder, sign = sign, valuetype = valueType, 
                    formula_factor = factor, formula_offset = offset, minimum = minimum, maximum = maximum, unit = unit, 
                    comment = cmt
                )
                self.session.add(ss)
                srid = ss.rid
                ms = Message_Signal(offset = startBit, multiplexor_signal = multiplexorSignal, 
                    multiplex_dependent = multiplexDependent, multiplexor_value = multiplexorValue)
                self.session.add(ms)
                ms.signal = ss
                mm.signals.append(ms)
                self.session.flush()

                """
                # create parent, append a child via association
                p = Parent()
                a = Association(extra_data="some data")
                a.child = Child()
                p.children.append(a)
                """
                
                #self.insertReceivers(cur, mrid, srid, receiver)    # TODO: Implement!!!
