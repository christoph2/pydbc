#!/usr/bin/env python
# -*- coding: utf-8 -*-

__copyright__ = """
   pySART - Simplified AUTOSAR-Toolkit for Python.

   (C) 2010-2020 by Christoph Schueler <cpu12.gems.googlemail.com>

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

from pydbc.db import BusType

from pydbc.db.model import (
    Dbc_Version, Message, Message_Signal, Network, Node, Signal, Value_Description, 
    Valuetable, EnvironmentVariablesData, EnvVar, Attribute_Definition, Attribute_Value,
    Node_TxMessage, Node_RxSignal, Category_Definition, Category_Value, AttributeRel_Value,
    Signal_Group_Signal, Signal_Group, Vndb_Protocol
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

    def __init__(self, db):
        super(DbcLoader, self).__init__(db)
        self.comments = Comments()

    def _insertValues(self, tree):
        self.insertVersion(tree['version'])
        self.insertEnvironmentVariablesData(tree['environmentVariablesData'])
        self.insertComments(tree['comments'])
        self.insertValueTables(tree['valueTables'])
        self.insertNetwork()
        self.insertNodes(tree['nodes'])
        valueTypes = self.processExtendedSignalValueTypes(tree['signalExtendedValueTypeList'])
        self.insertMessages(tree['messages'], valueTypes)
        self.insertEnvironmentVariables( tree['environmentVariables'])
        self.insertMessageTransmitters(tree['messageTransmitters'])
        self.insertValueDescriptions(tree['valueDescriptions'])
        defaults = tree['attributeDefaults']
        self.insertAttributeDefinitions(tree['attributeDefinitions'], defaults)
        self.insertAttributes(tree['attributeValues'])
        defaults = tree['relativeAttributeDefaults']
        self.insertAttributeDefinitions(tree['relativeAttributeDefinitions'], defaults)
        self.insertRelativeAttributes(tree['relativeAttributeValues'])
        self.insertSignalGroups(tree['signalGroups'])
        self.insertCategoryDefinitions(tree['categoryDefinitions'])
        self.insertCategoryValues(tree['categories'])
        self.session.commit()

    def processExtendedSignalValueTypes(self, valueTypes):
        keyFunc = lambda k: k['messageID']
        result = dict()
        valueTypes = sorted(valueTypes, key = keyFunc)
        for group in itertools.groupby(valueTypes, keyFunc):
            key, grouper = group
            result[key] = {}
            for item in grouper:
                result[key][item['signalName']] = item['valueType']
        return result

    def insertVersion(self, version):
        network = 0 ## TODO: Real value!!!
        vers = Dbc_Version(version_string = version, network = network)
        self.session.add(vers)
        self.session.flush()

    def insertNetwork(self, specific = None):
        comment = self.comments.network()
        network = Network(name = self.db.dbname, comment = comment)
        self.session.add(network)
        proto = Vndb_Protocol(network = network, name = BusType.CAN.name, specific = specific)
        self.session.add(proto)
        self.session.flush()

    def insertValueTables(self, tables):
        for table in tables:
            name = table['name']
            description = table['description']
            vt = Valuetable(name = name)
            self.session.add(vt)
            self.session.flush()
            self.insertValueDescription(vt.rid, description)
            
    def insertValueDescription(self, rid, description):
        for desc, value in description:
            vd = Value_Description(valuetable_id = rid, value = value, value_description = desc)
            self.session.add(vd)
        self.session.flush()

    def insertEnvironmentVariables(self, vars):
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
            for node in accessNodes:
                nn = self.session.query(Node).filter(Node.name == node).one()
                envVar.accessingNodes.append(nn)
        self.session.flush()

    def get_signal_by_name(self, messageID, name):
        res = self.session.query(Signal.rid).join(Message_Signal).join(Message).\
                filter(Message.message_id == messageID, Signal.name == name).first()
        return res[0]
        #    sq = self.session.query(Message.rid).filter(Message.message_id == messageID)
        #    query = self.session.query(Message_Signal.signal_id).join(Signal).filter(Signal.name == name, Message_Signal.message_id == sq)
        #    print("NEW_Q", query, query.all())
       
        #return cur.execute("""SELECT t1.RID FROM signal AS t1, Message_Signal AS t2 where
        #    t1.RID = t2.signal AND t1.name = ? AND t2.message = (SELECT RID FROM message
        #    WHERE message_id = ?)""", [name, messageID]
        #).fetchone()[0]

    def insertValueDescriptions(self, descriptions):    # TODO: Optimize!!!
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
            self.session.flush()
            self.insertValueDescription(vt.rid, description)
        self.session.flush()

    def insertReceivers(self, messageId, signalId, receiver):
        SignalReceivers = set()
        for rcv in receiver:
            nodeId = self.session.query(Node.rid).filter(Node.name == rcv).scalar()
            if not (messageId, signalId, nodeId) in SignalReceivers:
                rxs = Node_RxSignal(node_id = nodeId, message_id = messageId, signal_id = signalId)
                self.session.add(rxs)
            SignalReceivers.add((messageId, signalId, nodeId))
        self.session.flush()

    def insertComments(self, comments):
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

    def insertEnvironmentVariablesData(self, data):
        for item in data:
            name = item['name']
            value = item['value']
            evd = EnvironmentVariablesData(name = name, value = value)
            self.session.add(evd)
            print(evd)
        self.session.flush()

    def insertCategoryDefinitions(self, catagories):
        for category in catagories:
            cd = Category_Definition(name = category['name'], key = category['category'], level = category['value'])
            self.session.add(cd)
            print(cd)
        self.session.flush()

    def insertCategoryValues(self, catagories):
        for category in catagories:
            attrType = category['type']
            catId = category['category']
            if attrType == 'BU':
                nodeName = category['nodeName']
                objType = CategoryType.NODE
                rid = self.session.query(Node.rid).filter(Node.name == nodeName).scalar()
            elif attrType == 'BO':
                objType = CategoryType.MESSAGE
                messageID = category['messageID']
                rid = self.session.query(Message.rid).filter(Message.message_id == messageID).scalar()
            elif attrType == 'EV':
                envVarname = category['envVarname']
                objType = CategoryType.ENV_VAR
                rid = self.session.query(EnvVar.rid).filter(EnvVar.name == envVarname).scalar()
            cv = Category_Value(object_id = rid, category_definition_id = catId, objecttype = objType)
            self.session.add(cv)
            print(cv)
        self.session.flush()

    def insertAttributeDefinitions(self, attrs, defaults):
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
            ad = Attribute_Definition(name = name, objecttype = objType, valuetype = valueType, minimum = minimum,
                maximum = maximum, enumvalues = enumvalues, default_number = defaultNumber, default_string = defaultString)
            self.session.add(ad)
            self.session.flush()

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

    def insertAttributes(self, attrs):
        for attr in attrs:
            stringValue = None
            numValue = None
            value = attr['attributeValue']
            if isinstance(value, str):
                stringValue = value
            else:
                numValue = value
            ad = self.session.query(Attribute_Definition).filter(Attribute_Definition.name == attr['name']).one()
            attrType = self.getAttributeType(attr['attributeType'])
            if attrType == AttributeType.MESSAGE:
                rid = self.session.query(Message.rid).filter(Message.message_id == attr['messageID']).scalar()
            elif attrType == AttributeType.SIGNAL:
               rid = self.get_signal_by_name(attr['messageID'], attr['signalName'])
            elif attrType == AttributeType.NODE:
                rid = self.session.query(Node.rid).filter(Node.name == attr['nodeName']).scalar()
            elif attrType == AttributeType.ENV_VAR:
                rid = self.session.query(EnvVar.rid).filter(EnvVar.name == attr['envVarname']).scalar()
            elif attrType == AttributeType.NETWORK:
                rid = 0
            else:
                rid = 0
            av = Attribute_Value(object_id = rid, attribute_definition = ad, num_value = numValue, string_value = stringValue)
            self.session.add(av)
            self.session.flush()

    def insertRelativeAttributes(self, attrs):
        for attr in attrs:
            attributeName = attr['attributeName']
            attributeValue = attr['attributeValue']
            attrributeType = self.getAttributeType(attr['attributeType'])
            aid = self.session.query(Attribute_Definition).filter(Attribute_Definition.name == attr['attributeName']).scalar()
            nodeId = self.session.query(Node.rid).filter(Node.name == attr['nodeName']).scalar()
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
                rid = self.session.query(EnvVar.rid).filter(EnvVar.name == evName).scalar()
                #optOid2 = ???
            elif attrributeType == AttributeType.REL_NODE:
                messageID = parent['messageID']
                optOid2 = messageID
                rid = self.session.query(Message.rid).filter(Message.message_id == messageID).scalar()
            
            arv = AttributeRel_Value(object_id = rid, attribute_definition = aid, num_value = numValue,
                string_value = stringValue, opt_object_id_1 = optOid1, opt_object_id_2 = optOid2
            )
            self.session.add(arv)
            self.session.flush()

    def insertSignalGroups(self, signalGroups):
        for group in signalGroups:
            messageID = group['messageID']
            gValue = group['gvalue']
            signalNames = group['signals']
            groupName = group['groupName']
            msg = self.session.query(Message).filter(Message.message_id == messageID).first()
            sg = Signal_Group(name = groupName, value = gValue, message = msg)
            self.session.add(sg)
            self.session.flush()
            print("SIGNAL-GROUP", group)
            for signalName in signalNames:
                signal = self.session.query(Signal).join(Message_Signal).join(Message).\
                filter(Message.message_id == messageID, Signal.name == signalName).first()
                sgs = Signal_Group_Signal(signal_group = sg, message = msg, signal = signal)
                self.session.add(sgs)
            self.session.flush()

    def insertNodes(self, nodes):
        nodeSet = set()
        for node in nodes:
            comment = self.comments.node(node)
            if not node in nodeSet:
                nn = Node(name = node, comment = comment)
                self.session.add(nn)
            nodeSet.add(node)
        self.session.flush()

    def insertMessageTransmitters(self, transmitters):
        for transmitter in transmitters:
            mid = self.session.query(Message).filter(Message.message_id == transmitter['messageID']).scalar()
            for name in transmitter['transmitters']:
                nid = self.session.query(Node).filter(Node.name == name).scalar()
                ntm = Node_TxMessage(node = nid, message = mid)
                self.session.add(ntm)
        self.session.flush()

    def insertMessages(self, messages, valueTypes):
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
                
                self.insertReceivers(mm.rid, ss.rid, receiver)    # TODO: Implement!!!
