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


import re

from pydbc import parser

from pydbc.types import AttributeType, BusType, CategoryType, ValueType

from pydbc.db.model import (
    Dbc_Version, Message, Message_Signal, Network, Node, Signal, Value_Description,
    Valuetable, EnvironmentVariablesData, EnvVar, Attribute_Definition, Attribute_Value,
    Node_TxMessage, Node_RxSignal, Category_Definition, Category_Value, AttributeRel_Value,
    Signal_Group_Signal, Signal_Group, Vndb_Protocol, Object_Valuetable
)


## Attributes
##  GenSigStartValue    ==> to set initial value until first message is received.
##  GenMsgCycleTime     ==> to set transmission rate

"""
Before moving on, note that J1939 is a bit special in regards to the CAN DBC file format:
- The ID is extended 29 bit - in DBC context, this means that the the leading bit of the ID is "flipped" and needs to be re-flipped
- Secondly, the relevant ID is the PGN, i.e. a sub part of the CAN ID (start bit 9, length 18)
"""

DIGITS = re.compile(r'(\d+)')

CO_MPX = re.compile(r"^(?P<multiplexed>m)(?P<value>\d+)(?P<multiplexer>M)$")


def extractAccessType(value):
    match = DIGITS.search(value)
    if match:
        return int(match.group())
    else:
        return None


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


class DbcListener(parser.BaseListener):
    """

    """

    def __init__(self, database, *args, **kws):
        super(DbcListener, self).__init__(database, *args, **kws)
        self.insertNetwork()

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

    def get_signal_by_name(self, messageID, signal_name):
        res = self.db.session.query(Signal.rid).join(Message_Signal).join(Message).\
                filter(Message.message_id == messageID, Signal.name == signal_name).first()
        if res:
            return res.rid
        else:
            return []

    def insertReceivers(self, messageId, signalId, receiver):
        SignalReceivers = set()
        for rcv in receiver:
            nodeId = self.db.session.query(Node.rid).filter(Node.name == rcv).scalar()
            if not (messageId, signalId, nodeId) in SignalReceivers:
                rxs = Node_RxSignal(node_id = nodeId, message_id = messageId, signal_id = signalId)
                self.db.session.add(rxs)
            SignalReceivers.add((messageId, signalId, nodeId))
        self.db.session.flush()

    def insertValueDescription(self, rid, description):
        objs = []
        for desc, value in description:
            vd = Value_Description(valuetable_id = rid, value = value, value_description = desc)
            objs.append(vd)
        self.db.session.add_all(objs)
        self.db.session.flush()

    def insertAttributeDefinitions(self, ctx):
        ctx.value = [x.value for x in ctx.items]
        for attr in ctx.value:
            attrType = attr['type']
            name = attr['name']
            vt = attr['value']['type']
            values = attr['value']['value']
            minimum = None
            maximum = None
            enumvalues = None
            defaultNumber = None
            defaultString = None
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
            elif vt == 'HEX':
                valueType = ValueType.HEX
                minimum, maximum = values
            elif vt == 'FLOAT':
                valueType = ValueType.FLOAT
                minimum, maximum = values
            elif vt == 'STRING':
                valueType = ValueType.STRING
            elif vt == 'ENUM':
                valueType = ValueType.ENUM
                enumvalues = ';'.join(values)
            ad = Attribute_Definition(name = name, objecttype = objType, valuetype = valueType, minimum = minimum,
                maximum = maximum, enumvalues = enumvalues)
            self.db.session.add(ad)
        self.db.session.flush()

    def insertAttributeDefaults(self, ctx):
        defaults = {}
        for item in ctx.items:
            name, value = item.value
            defaults[name] = value
            ad = self.db.session.query(Attribute_Definition).filter(Attribute_Definition.name == name).first()
            if not ad:
                self.logger.error("Error while inserting attribute default values: attribute '{}' does not exist.".format(name))
                continue
            if ad.valuetype in (ValueType.INT, ValueType.HEX, ValueType.FLOAT):
                ad.default_number = value
            elif ad.valuetype in (ValueType.STRING, ValueType.ENUM):
                ad.default_string = value
        self.db.session.flush()
        ctx.value = defaults

    def insertNetwork(self, specific = None):
        network = Network(name = self.db.dbname)
        self.db.session.add(network)
        proto = Vndb_Protocol(network = network, name = BusType.CAN.name, specific = specific)
        self.db.session.add(proto)
        self.db.session.flush()
        self.network_id = network.rid

    def exitDbcfile(self, ctx):
        self.db.session.commit()
        self.value = dict(
            version = ctx.version().value,
            newSymbols = ctx.newSymbols().value,
            bitTiming = ctx.bitTiming().value,
            nodes = ctx.nodes().value,
            valueTables = ctx.valueTables().value,
            messages = ctx.messages().value,
            messageTransmitters = ctx.messageTransmitters().value,
            environmentVariables = ctx.environmentVariables().value,
            environmentVariablesData = ctx.environmentVariablesData().value,
            signalTypes = ctx.signalTypes().value,
            comments = ctx.comments().value,
            attributeDefinitions = ctx.attributeDefinitions().value,
            relativeAttributeDefinitions = ctx.relativeAttributeDefinitions().value,
            attributeDefaults = ctx.attributeDefaults().value,
            relativeAttributeDefaults = ctx.relativeAttributeDefaults().value,
            attributeValues = ctx.attributeValues().value,
            relativeAttributeValues = ctx.relativeAttributeValues().value,
            objectValueTables = ctx.objectValueTables().value,
            categoryDefinitions = ctx.categoryDefinitions().value,
            categories = ctx.categories().value,
            signalGroups = ctx.signalGroups().value,
            signalExtendedValueTypeList = ctx.signalExtendedValueTypeList().value

        )

    def exitMessageTransmitters(self, ctx):
        ctx.value = [x.value for x in ctx.items]
        for transmitter in ctx.value:
            mid = self.db.session.query(Message).filter(Message.message_id == transmitter['messageID']).scalar()
            for name in transmitter['transmitters']:
                nid = self.db.session.query(Node).filter(Node.name == name).scalar()
                ntm = Node_TxMessage(node = nid, message = mid)
                self.db.session.add(ntm)
        self.db.session.flush()

    def exitMessageTransmitter(self, ctx):
        transmitters = self.getValue(ctx.tx)
        ctx.value = dict(messageID = self.getValue(ctx.messageID), transmitters = transmitters)

    def exitSignalExtendedValueTypeList(self, ctx):
        ctx.value = [x.value for x in ctx.items]
        valueTypes = ctx.value
        for item in valueTypes:
            msgId = item['messageID']
            sigName = item['signalName']
            vt = item['valueType']
            srid = self.get_signal_by_name(msgId, sigName)
            signal = self.db.session.query(Signal).filter(Signal.rid == srid).one()
            signal.valuetype = vt
        self.db.session.flush()

    def exitSignalExtendedValueType(self, ctx):
        messageID = self.getValue(ctx.messageID)
        signalName = self.getValue(ctx.signalName)
        valType = self.getValue(ctx.valType)
        if not valType in (0, 1, 2, 3):
            self.logger.error("ValueType must be in range [0..3] - got '{}'.".format(valType))
            valType = 0
        ctx.value = dict(messageID = messageID, signalName = signalName, valueType = valType)

    def exitMessages(self, ctx):
        ctx.value = [x.value for x in ctx.items]
        for msg in ctx.value:
            name = msg['name']
            mid = msg['messageID']
            dlc = msg['dlc']
            signals = msg['signals']
            transmitter = msg['transmitter']
            tid = self.db.session.query(Node.rid).filter(Node.name == transmitter).scalar()
            mm = Message(name = name, message_id = mid, dlc = dlc, sender = tid)
            self.db.session.add(mm)
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

                multiplexorSignal = None
                multiplexDependent = None
                multiplexorValue = None
                multiplexerIndicator = signal['multiplexerIndicator']
                if multiplexerIndicator:
                    match = CO_MPX.match(multiplexerIndicator)
                    if match:
                        gd = match.groupdict()
                        print("MPX:", gd)
                        gd['multiplexed'] == 'm'
                        multiplexorValue = gd['value']
                        multiplexorSignal = 1 if gd['multiplexer'] == 'M' else 0
                        multiplexDependent = 0 if multiplexorSignal else 1

                    """
                    multiplexorSignal = 1 if multiplexerIndicator == 'M' else 0
                    if multiplexorSignal:
                        multiplexDependent = 0
                        multiplexorValue = None
                    else:
                        multiplexDependent = 1

                        try:
                            multiplexorValue = int(multiplexerIndicator[1 : ])
                        except Exception as e:
                            print(str(e), "MPX:", multiplexerIndicator)
                else:
                    multiplexorSignal = None
                    multiplexDependent = None
                    multiplexorValue = None
                     """

                ss = Signal(name = name, bitsize = signalSize, byteorder = byteOrder, sign = sign,
                    formula_factor = factor, formula_offset = offset, minimum = minimum, maximum = maximum, unit = unit
                )
                self.db.session.add(ss)
                srid = ss.rid
                ms = Message_Signal(offset = startBit, multiplexor_signal = multiplexorSignal,
                    multiplex_dependent = multiplexDependent, multiplexor_value = multiplexorValue,
                    signal = ss, message = mm)
                self.db.session.add(ms)
                self.db.session.flush()
                self.insertReceivers(mm.rid, ss.rid, receiver)

    def exitMessage(self, ctx):
        ctx.value = dict(messageID = self.getValue(ctx.messageID), name = self.getValue(ctx.messageName),
            dlc = self.getValue(ctx.messageSize), transmitter = self.getTerminal(ctx.transmt),
            signals = [x.value for x in ctx.sgs]
        )

    def exitSignal(self, ctx):
        byteOrder = self.getValue(ctx.byteOrder)
        if not byteOrder in (0, 1):
            self.logger.error("Error while parsing signal '{}': byteorder must be either 0 or 1".format(ctx.signalName.value))
            byteOrder = 0
        name = self.getValue(ctx.signalName)
        startBit = self.getValue(ctx.startBit)
        signalSize = self.getValue(ctx.signalSize)
        st = self.getTerminal(ctx.sign)
        sign = None if st is None else -1 if st == '-' else +1
        factor = self.getValue(ctx.factor)
        offset = self.getValue(ctx.offset)
        minimum = self.getValue(ctx.minimum)
        maximum = self.getValue(ctx.maximum)
        unit = self.getValue(ctx.unit)
        receiver = self.getValue(ctx.rcv) or []
        ctx.value = dict(name = name, startBit = startBit, signalSize = signalSize,
            byteOrder = byteOrder, sign = sign, factor = factor, offset = offset,
            minimum = minimum, maximum = maximum, unit = unit, receiver = receiver,
            multiplexerIndicator = ctx.mind.value if ctx.mind else None
        )

    def exitReceiver(self, ctx):
        ctx.value = [ctx.fid.text] + [x.value for x in ctx.ids]

    def exitTransmitter(self, ctx):
        ctx.value = [x.value for x in ctx.ids]

    def exitMultiplexerIndicator(self, ctx):
        ctx.value = self.getValue(ctx.mind)

    def exitValueTables(self, ctx):
        ctx.value = [x.value for x in ctx.items]
        for table in ctx.value:
            name = table['name']
            description = table['description']
            vt = Valuetable(name = name)
            self.db.session.add(vt)
            self.db.session.flush()
            self.insertValueDescription(vt.rid, description)
        self.db.session.flush()

    def exitValueTable(self, ctx):
        ctx.value = dict(name = ctx.name.value, description = [x.value for x in ctx.desc])

    def exitValueDescription(self, ctx):
        ctx.value = (ctx.name.value, ctx.val.value, )

    def exitNodes(self, ctx):
        ctx.value = [x.value for x in ctx.ids]
        nodeSet = set(['Vector__XXX'])
        for name in ctx.value:
            if not name in nodeSet:
                nn = Node(name = name)
                self.db.session.add(nn)
            nodeSet.add(name)
        self.db.session.flush()

    def exitBitTiming(self, ctx):
        ctx.value = dict(baudrate = self.getValue(ctx.baudrate), btr1 = self.getValue(ctx.btr1), btr2 = self.getValue(ctx.btr2))

    def exitNewSymbols(self, ctx):
        ctx.value = [x.text for x in ctx.ids]

    def exitVersion(self, ctx):
        ctx.value = self.getValue(ctx.vs)
        version = ctx.value
        network = self.network_id
        vers = Dbc_Version(version_string = version, network = network)
        self.db.session.add(vers)
        self.db.session.flush()

    def exitObjectValueTables(self, ctx):
        ctx.value = [x.value for x in ctx.items]
        for table in ctx.value:
            #print("OVT:", table, end = "\n\n")
            tp = table['type']
            description = table['description']
            if tp == 'SG':
                object_rid = table['messageID']
                name = table['signalName']
                otype = 0
            elif tp == 'EV':
                name = table['envVarName']
                otype = 1
                object_rid = self.db.session.query(EnvVar.rid).filter(EnvVar.name == name).scalar()
            vt = Valuetable(name = name)
            self.db.session.add(vt)
            self.db.session.flush()
            ovt = Object_Valuetable(object_type= otype, object_rid = object_rid, valuetable_id = vt.rid)
            self.db.session.add(ovt)
            self.db.session.flush()
            self.insertValueDescription(vt.rid, description)

    def exitObjectValueTable(self, ctx):
        items = [x.value for x in ctx.items]
        if ctx.messageID:
            messageID = ctx.messageID.value
            signalName = ctx.signalName.value
            di = dict(messageID = messageID, signalName = signalName)
            tp = "SG"
        else:
            envVarName = ctx.envVarName.value
            di = dict(envVarName = envVarName)
            tp = "EV"
        ctx.value = dict(type = tp, description = items, **di)

    def exitEnvironmentVariables(self, ctx):
        ctx.value = [x.value for x in ctx.evs]
        for var in ctx.value:
            unit = var['unit']
            initialValue = var['initialValue']
            accessNodes = var['accessNodes']
            accessType = var['accessType']
            minimum = var['minimum']
            maximum = var['maximum']
            envId = var['envId']
            varType = var['varType']
            name = var['name']
            dataSize = self.db.session.query(EnvironmentVariablesData.value).filter(EnvironmentVariablesData.name == name).scalar()
            envVar = EnvVar(name = name, type = varType, unit = unit, minimum = minimum, maximum = maximum,
                access = accessType, startup_value = initialValue, size = dataSize)
            self.db.session.add(envVar)
            for node in accessNodes:
                nn = self.db.session.query(Node).filter(Node.name == node).one()
                envVar.accessingNodes.append(nn)
        self.db.session.flush()

    def exitEnvironmentVariable(self, ctx):
        accessType = extractAccessType(ctx.DUMMY_NODE_VECTOR().getText())

        ctx.value = dict(name = self.getValue(ctx.name), varType = self.getValue(ctx.varType),
            minimum = self.getValue(ctx.minimum), maximum = self.getValue(ctx.maximum), unit = self.getValue(ctx.unit),
            initialValue = self.getValue(ctx.initialValue), envId = self.getValue(ctx.envId),
            accessType = accessType, accessNodes = self.getValue(ctx.accNodes)
        )

    def exitAccessNodes(self, ctx):
        nodes = [x.value for x in ctx.items]
        ctx.value = nodes

    def exitEnvironmentVariablesData(self, ctx):
        ctx.value = [x.value for x in ctx.evars]
        for item in ctx.value:
            print("EVD", item)
            name = item['name']
            value = item['value']
            evd = EnvironmentVariablesData(name = name, value = value)
            self.db.session.add(evd)
        self.db.session.flush()

    def exitEnvironmentVariableData(self, ctx):
        ctx.value = dict(name = self.getValue(ctx.varname), value = self.getValue(ctx.value))

    def exitSignalTypes(self, ctx):
        ctx.value =[x.value for x in ctx.sigTypes]
        print("SIGNAL-TYPES", ctx.value)

    def exitSignalType(self, ctx):
        ctx.value = dict(name = self.getValue(ctx.signalTypeName), size = self.getValue(ctx.signalSize),
            byteOrder = self.getValue(ctx.byteOrder), valueType = self.getValue(ctx.valueType),
            factor = self.getValue(ctx.factor), offset = self.getValue(ctx.offset), minimum = self.getValue(ctx.minimum),
            maximum = self.getValue(ctx.maximum), unit = self.getValue(ctx.unit), defaultValue = self.getValue(ctx.defaultValue),
            valTable = self.getValue(ctx.valTable),
        )

    def exitComments(self, ctx):
        ctx.value = [x.value for x in ctx.items]
        for comment in ctx.value:
            tp = comment['type']
            text = comment['comment']
            key = comment['key']
            if tp == 'BU':
                obj = self.db.session.query(Node).filter(Node.name == key).one()
                obj.comment = text
            elif tp == 'BO':
                obj = self.db.session.query(Message).filter(Message.message_id == key).one()
                obj.comment = text
            elif tp == 'SG':
                rid = self.get_signal_by_name(*key)
                if not rid:
                    self.logger.error("Error while inserting comments: message signal '{}' does not exist.".format(key))
                    continue
                obj = self.db.session.query(Signal).filter(Signal.rid == rid).one()
                obj.comment = text
            elif tp == 'EV':
                obj = self.db.session.query(EnvVar).filter(EnvVar.name == key).one()
                obj.comment = text
            else:   # NW !?
                obj = self.db.session.query(Network).filter(Network.rid == self.network_id).one()
                obj.comment = text
                print("NW-CMT", comment, "\n\t", obj)
        self.db.session.flush()

    def exitComment(self, ctx):
        comment = self.getValue(ctx.s)
        if ctx.c0:
            tp = "BU"
            key = self.getValue(ctx.c0)
        elif ctx.i1:
            tp = "BO"
            key = self.getValue(ctx.i1)
        elif ctx.i2:
            tp = "SG"
            key = (self.getValue(ctx.i2), self.getValue(ctx.c2), )
        elif ctx.c3:
            tp = "EV"
            key = self.getValue(ctx.c3)
        else:
            tp = "NETWORK"
            key = None
        ctx.value = dict(type = tp, key = key, comment = comment)

    def exitAttributeDefinitions(self, ctx):
        self.insertAttributeDefinitions(ctx)

    def exitAttributeDefinition(self, ctx):
        objectType = self.getTerminal(ctx.objectType)
        attributeName = self.getValue(ctx.attrName)
        attributeValue = self.getValue(ctx.attrValue)
        ctx.value = dict(type = objectType, name = attributeName, value = attributeValue)

    def exitRelativeAttributeDefinitions(self, ctx):
        ctx.value = [x.value for x in ctx.items]
        self.insertAttributeDefinitions(ctx)

    def exitRelativeAttributeDefinition(self, ctx):
        objectType = self.getTerminal(ctx.objectType)
        attributeName = self.getValue(ctx.attrName)
        attributeValue = self.getValue(ctx.attrValue)
        ctx.value = dict(type = objectType, name = attributeName, value = attributeValue)

    def exitAttributeValueType(self, ctx):
        if ctx.i00:
            tp = "INT"
            value = (self.getValue(ctx.i00), self.getValue(ctx.i01), )
        elif ctx.i10:
            tp = "HEX"
            value = (self.getValue(ctx.i10), self.getValue(ctx.i11), )
        elif ctx.f0:
            tp = "FLOAT"
            value = (float(self.getValue(ctx.f0)), float(self.getValue(ctx.f1)), )
        elif ctx.s0:
            tp = "STRING"
            value = None
        elif ctx.efirst:
            tp = "ENUM"
            efirst = [self.getValue(ctx.efirst)]
            eitems = [x.value for x in ctx.eitems]
            value = efirst + eitems
        ctx.value = dict(type = tp, value = value)

    def exitAttributeDefaults(self, ctx):
        self.insertAttributeDefaults(ctx)

    def exitAttributeDefault(self, ctx):
        name = self.getValue(ctx.n)
        value = self.getValue(ctx.v)
        ctx.value = (name, value)

    def exitRelativeAttributeDefaults(self, ctx):
        self.insertAttributeDefaults(ctx)

    def exitRelativeAttributeDefault(self, ctx):
        name = self.getValue(ctx.n)
        value = self.getValue(ctx.v)
        ctx.value = (name, value)

    def exitAttributeValue(self, ctx):
        if ctx.s:
            ctx.value = self.getValue(ctx.s)
        elif ctx.n:
            ctx.value = self.getValue(ctx.n)

    def exitAttributeValues(self, ctx):
        ctx.value = [x.value for x in ctx.items]
        for attr in ctx.value:
            stringValue = None
            numValue = None
            value = attr['attributeValue']
            if isinstance(value, str):
                stringValue = value
            else:
                numValue = value
            aname = attr['name']
            ad = self.db.session.query(Attribute_Definition).filter(Attribute_Definition.name == attr['name']).one()
            attrType = self.getAttributeType(attr['attributeType'])
            if attrType == AttributeType.MESSAGE:
                rid = self.db.session.query(Message.rid).filter(Message.message_id == attr['messageID']).scalar()
            elif attrType == AttributeType.SIGNAL:
               rid = self.get_signal_by_name(attr['messageID'], attr['signalName']) #
            elif attrType == AttributeType.NODE:
                rid = self.db.session.query(Node.rid).filter(Node.name == attr['nodeName']).scalar()
            elif attrType == AttributeType.ENV_VAR:
                rid = self.db.session.query(EnvVar.rid).filter(EnvVar.name == attr['envVarname']).scalar()
            elif attrType == AttributeType.NETWORK:
                rid = 0
            else:
                rid = 0
            av = Attribute_Value(object_id = rid, attribute_definition = ad, num_value = numValue, string_value = stringValue)
            self.db.session.add(av)
        self.db.session.flush()

    def exitAttributeValueForObject(self, ctx):
        attributeName = self.getValue(ctx.attributeName)
        if ctx.nodeName:
            nodeName = self.getValue(ctx.nodeName)
            attrValue = self.getValue(ctx.buValue)
            di = dict(attributeType = 'BU', nodeName = nodeName)
        elif ctx.mid1:
            mid1 = self.getValue(ctx.mid1)
            attrValue = self.getValue(ctx.boValue)
            di = dict(attributeType = 'BO', messageID = mid1)
        elif ctx.mid2:
            mid2 = self.getValue(ctx.mid2)
            signalName = self.getValue(ctx.signalName)
            attrValue = self.getValue(ctx.sgValue)
            di = dict(attributeType = 'SG', messageID = mid2, signalName = signalName)
        elif ctx.evName:
            evName = self.getValue(ctx.evName)
            attrValue = self.getValue(ctx.evValue)
            di = dict(attributeType = 'EV', envVarname = evName)
        else:
            evName = None
            attrValue = self.getValue(ctx.attrValue)
            di = dict(attributeType = "NETWORK")
        ctx.value = dict(name = attributeName, attributeValue = attrValue, **di)

    def exitRelativeAttributeValues(self, ctx):
        items = [x.value for x in ctx.items]
        ctx.value = items
        for attr in items:
            attributeName = attr['attributeName']
            attributeValue = attr['attributeValue']
            attrributeType = self.getAttributeType(attr['attributeType'])
            aid = self.db.session.query(Attribute_Definition).filter(Attribute_Definition.name == attr['attributeName']).scalar()
            nodeId = self.db.session.query(Node.rid).filter(Node.name == attr['nodeName']).scalar()
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
                rid = self.db.session.query(EnvVar.rid).filter(EnvVar.name == evName).scalar()
                #optOid2 = ???
            elif attrributeType == AttributeType.REL_NODE:
                messageID = parent['messageID']
                optOid2 = messageID
                rid = self.db.session.query(Message.rid).filter(Message.message_id == messageID).scalar()
            arv = AttributeRel_Value(object_id = rid, attribute_definition = aid, num_value = numValue,
                string_value = stringValue, opt_object_id_1 = optOid1, opt_object_id_2 = optOid2
            )
            self.db.session.add(arv)
        self.db.session.flush()

    def exitRelativeAttributeValueForObject(self, ctx):
        attrType = self.getTerminal(ctx.attrType)
        attributeName = self.getValue(ctx.attributeName)
        nodeName = self.getValue(ctx.nodeName)
        if attrType == "BU_BO_REL_":
            messageID = self.getValue(ctx.nodeAddress)
            attributeType = "REL_NODE"
            parent = dict(messageID = messageID)
            attrValue = self.getValue(ctx.attrValue)
        elif attrType == "BU_SG_REL_":
            messageID = self.getValue(ctx.messageID)
            signalName = self.getValue(ctx.signalName)
            attributeType = "REL_SIGNAL"
            parent = dict(messageID = messageID, signalName = signalName)
            attrValue = self.getValue(ctx.attrValue)
        elif attrType == "BU_EV_REL_":
            evName = ctx.evName.value
            attributeType = "REL_ENV_VAR"
            parent = dict(evName = evName)
            attrValue = self.getValue(ctx.evValue)
        ctx.value = dict(
            attributeType = attributeType, attributeName = attributeName, attributeValue = attrValue,
            nodeName = nodeName, parent = parent
        )

    def exitSignalGroups(self, ctx):
        items = [x.value for x in ctx.items]
        ctx.value = items
        for group in ctx.value:
            messageID = group['messageID']
            gValue = group['gvalue']
            signalNames = group['signals']
            groupName = group['groupName']
            msg = self.db.session.query(Message).filter(Message.message_id == messageID).first()
            sg = Signal_Group(name = groupName, value = gValue, message = msg)
            self.db.session.add(sg)
            self.db.session.flush()
            for signalName in signalNames:
                signal = self.db.session.query(Signal).join(Message_Signal).join(Message).\
                filter(Message.message_id == messageID, Signal.name == signalName).first()
                sgs = Signal_Group_Signal(signal_group = sg, message = msg, signal = signal)
                self.db.session.add(sgs)
        self.db.session.flush()

    def exitSignalGroup(self, ctx):
        messageID = self.getValue(ctx.messageID)
        groupName = self.getValue(ctx.groupName)
        gvalue = self.getValue(ctx.gvalue)
        signals = [x.value for x in ctx.signals]
        ctx.value = dict(messageID = messageID, groupName = groupName, gvalue = gvalue, signals = signals)

    def exitCategoryDefinitions(self, ctx):
        ctx.value = [x.value for x in ctx.items]
        for category in ctx.value:
            print("CAT-DEF", category)
            cd = Category_Definition(name = category['name'], key = category['category'], level = category['value'])
            self.db.session.add(cd)
        self.db.session.flush()

    def exitCategoryDefinition(self, ctx):
        ctx.value = dict(name = self.getValue(ctx.name), category = self.getValue(ctx.cat), value = self.getValue(ctx.num))

    def exitCategories(self, ctx):
        ctx.value = [x.value for x in ctx.items]
        for category in ctx.value:
            print("CAT-VALUE", category)
            attrType = category['type']
            catId = category['category']
            if attrType == 'BU':
                nodeName = category['nodeName']
                objType = CategoryType.NODE
                rid = self.db.session.query(Node.rid).filter(Node.name == nodeName).scalar()
            elif attrType == 'BO':
                objType = CategoryType.MESSAGE
                messageID = category['messageID']
                rid = self.db.session.query(Message.rid).filter(Message.message_id == messageID).scalar()
            elif attrType == 'EV':
                envVarname = category['envVarname']
                objType = CategoryType.ENV_VAR
                rid = self.db.session.query(EnvVar.rid).filter(EnvVar.name == envVarname).scalar()
            cv = Category_Value(object_id = rid, category_definition_id = catId, objecttype = objType)
            self.db.session.add(cv)
            print(cv)
        self.db.session.flush()

    def exitCategory(self, ctx):
        category = self.getValue(ctx.cat)
        if ctx.nodeName:
            nodeName = self.getValue(ctx.nodeName)
            di = dict(type = 'BU', nodeName = nodeName)
        elif ctx.mid1:
            mid1 = self.getValue(ctx.mid1)
            di = dict(type = 'BO', messageID = mid1)
        elif ctx.evName:
            evName = self.getValue(ctx.evName)
            di = dict(type = 'EV', envVarname = evName)
        ctx.value = dict(category = category, **di)