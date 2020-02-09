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

from sqlalchemy.sql.expression import literal, bindparam
from sqlalchemy.ext import baked

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

CO_MPX = re.compile(r"^(?P<multiplexed>m)?(?P<value>\d+)?(?P<multiplexer>M)?$")


def extractAccessType(value):
    match = DIGITS.search(value)
    if match:
        return int(match.group())
    else:
        return None


class DbcListener(parser.BaseListener):
    """

    """

    def __init__(self, database, logLevel = 'INFO', *args, **kws):
        super(DbcListener, self).__init__(database, logLevel, *args, **kws)
        self.session = self.db.session
        self.bakery = baked.bakery()
        self.bake_queries()
        self.insertNetwork()

    def bake_queries(self):
        self.ATTRIBUTE_DEFINITION_BY_NAME = self.bakery(lambda session: self.session.query(Attribute_Definition).\
            filter(Attribute_Definition.name == bindparam('name')))
        self.MESSAGE_BY_MESSAGE_ID = self.bakery(lambda session: session.query(Message).filter(Message.message_id == bindparam('message_id')))
        self.NODE_BY_NAME = self.bakery(lambda session: session.query(Node).filter(Node.name == bindparam('name')))
        self.ENVVAR_BY_NAME = self.bakery(lambda session: session.query(EnvVar).filter(EnvVar.name == bindparam('name')))
        self.ENVDATA_BY_NAME = self.bakery(lambda session: session.query(EnvironmentVariablesData).filter(
            EnvironmentVariablesData.name == bindparam('name')))
        self.MESSAGE_SIGNAL_BY_NAME = self.bakery(lambda session: session.query(Signal.rid).join(Message_Signal).join(Message).\
                filter(Message.message_id == bindparam('messageID'), Signal.name == bindparam('signal_name')))
        self.NETWORK_BY_RID = self.bakery(lambda session: session.query(Network).filter(Network.rid == bindparam('rid')))
        self.SIGNAL_BY_RID = self.bakery(lambda session: session.query(Signal).filter(Signal.rid == bindparam('rid')))
        self.EXISTS_ATTRIBUTE_DEFINITION = self.bakery(lambda session: session.query(literal(True)).filter(
            Attribute_Definition.name == bindparam('name')))
        self.EXISTS_ATTRIBUTE_VALUE = self.bakery(lambda session: session.query(literal(True)).filter(
                Attribute_Value.object_id == bindparam('rid'), Attribute_Value.attribute_definition_id == bindparam('ad')))
        self.EXISTS_NETWORK = self.bakery(lambda session: session.query(literal(True)).filter(Network.name == bindparam('name')))
        self.EXISTS_NODE_RXSIGNAL = self.bakery(lambda session: session.query(literal(True)).filter(
                Node_RxSignal.node_id == bindparam('nodeId'),
                Node_RxSignal.message_id == bindparam('messageId'),
                Node_RxSignal.signal_id == bindparam('signalId')))
        self.EXISTS_VALUE_DESCRIPTION = self.bakery(lambda session: session.query(literal(True)).filter(
                Value_Description.valuetable_id == bindparam('rid'), Value_Description.value == bindparam('value')))
        self.MESSAGE_SIGNAL_BY_NAME2 = self.bakery(lambda session: session.query(Signal).join(Message_Signal).join(Message).\
            filter(Message.message_id == bindparam('messageID'), Signal.name == bindparam('signalName')))

    def log_insertion(self, table_name):
        self.logger.debug("Inserting values for '{}'.".format(table_name))

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
        res = self.MESSAGE_SIGNAL_BY_NAME(self.session).params(messageID = messageID,signal_name = signal_name).first()
        if res:
            return res.rid
        else:
            self.logger.error("Message signal '{}'::'{}' does not exist.".format(messageID, signal_name))
            return []

    def insertReceivers(self, messageId, signalId, receiver):
        self.log_insertion("Node_RxSignal")
        for rcv in receiver:
            res = self.NODE_BY_NAME(self.session).params(name = rcv).first()
            if res:
                nodeId = res.rid
            else:
                self.logger.error("While inserting signal receivers: node '{}' does not exist.".format(rcv))
                continue
            exists = self.EXISTS_NODE_RXSIGNAL(self.session).params(nodeId = nodeId, messageId = messageId,
                signalId = signalId).first()
            if exists:
                self.logger.error("While inserting signal receivers: receiver messageId: {} signalId: {} nodeId: {} already exists.".
                    format(messageId, signalId, nodeId)
                )
            else:
                rxs = Node_RxSignal(node_id = nodeId, message_id = messageId, signal_id = signalId)
                self.session.add(rxs)
        self.session.flush()

    def insertValueDescription(self, rid, description):
        objs = []
        for desc, value in description:
            exists = self.EXISTS_VALUE_DESCRIPTION(self.session).params(rid = rid, value = value).first()
            if exists:
                pass
            else:
                vd = Value_Description(valuetable_id = rid, value = value, value_description = desc)
                objs.append(vd)
        self.session.add_all(objs)
        self.session.flush()

    def insertAttributeDefinitions(self, ctx):
        self.log_insertion("Attribute_Definition")
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
            exists = self.EXISTS_ATTRIBUTE_DEFINITION(self.session).params(name = name).first()
            if exists:
                self.logger.error("While inserting attribute definitions: an attribute definition named '{}' already exists.".format(name))
            else:
                ad = Attribute_Definition(name = name, objecttype = objType, valuetype = valueType, minimum = minimum,
                                          maximum = maximum, enumvalues = enumvalues)
                self.session.add(ad)
        self.session.flush()

    def insertAttributeDefaults(self, ctx):
        self.log_insertion("Attribute_Defaults")
        defaults = {}
        for item in ctx.items:
            name, value = item.value
            defaults[name] = value
            ad = self.ATTRIBUTE_DEFINITION_BY_NAME(self.session).params(name = name).first()
            if not ad:
                self.logger.error("While inserting attribute default values: attribute '{}' does not exist.".format(name))
                continue
            if ad.valuetype in (ValueType.INT, ValueType.HEX, ValueType.FLOAT):
                ad.default_number = value
            elif ad.valuetype in (ValueType.STRING, ValueType.ENUM):
                ad.default_string = value
        self.session.flush()
        ctx.value = defaults

    def insertNetwork(self, specific = None):
        self.log_insertion("Network")
        name = self.db.dbname
        exists = self.EXISTS_NETWORK(self.session).params(name = name).first()
        if exists:
            self.logger.error("While inserting network: an network named '{}' already exists.".format(name))
            return
        network = Network(name = name)
        self.session.add(network)
        proto = Vndb_Protocol(network = network, name = BusType.CAN.name, specific = specific)
        self.session.add(proto)
        self.session.flush()
        self.network_id = network.rid

    def exitDbcfile(self, ctx):
        self.session.commit()
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
        self.log_insertion("Node_TxMessage")
        ctx.value = [x.value for x in ctx.items]
        for transmitter in ctx.value:
            msg = self.MESSAGE_BY_MESSAGE_ID(self.session).params(message_id = transmitter['messageID']).first()
            if not msg:
                self.logger.error("While inserting message transmitters: message '{}' does not exist.".format(transmitter['messageID']))
                continue
            for name in transmitter['transmitters']:
                node = self.NODE_BY_NAME(self.session).params(name = name).first()
                if not node:
                    self.logger.error("While inserting message transmitters: node '{}' does not exist.".format(name))
                    continue
                ntm = Node_TxMessage(node = node, message = msg)
                self.session.add(ntm)
        self.session.flush()

    def exitMessageTransmitter(self, ctx):
        transmitters = self.getValue(ctx.tx)
        ctx.value = dict(messageID = self.getValue(ctx.messageID), transmitters = transmitters)

    def exitSignalExtendedValueTypeList(self, ctx):
        self.log_insertion("SignalExtendedValueType")
        ctx.value = [x.value for x in ctx.items]
        valueTypes = ctx.value
        for item in valueTypes:
            msgId = item['messageID']
            sigName = item['signalName']
            vt = item['valueType']
            srid = self.get_signal_by_name(msgId, sigName)
            signal = self.SIGNAL_BY_RID(self.session).params(rid = srid).first()
            if not signal:
                self.logger.error("While inserting signal extended value types: signal '{}' does not exist.".format(srid))
                continue
            signal.valuetype = vt
        self.session.flush()

    def exitSignalExtendedValueType(self, ctx):
        messageID = self.getValue(ctx.messageID)
        signalName = self.getValue(ctx.signalName)
        valType = self.getValue(ctx.valType)
        if not valType in (0, 1, 2, 3):
            self.logger.error("While parsing signal extended value type: value type must be in range [0..3] - got '{}', using 0.".format(valType))
            valType = 0
        ctx.value = dict(messageID = messageID, signalName = signalName, valueType = valType)

    def exitMessages(self, ctx):
        self.log_insertion("Messages and Signals")
        ctx.value = [x.value for x in ctx.items]
        for msg in ctx.value:
            name = msg['name']
            mid = msg['messageID']
            dlc = msg['dlc']
            signals = msg['signals']
            transmitter = msg['transmitter']
            tx_node = self.NODE_BY_NAME(self.session).params(name = transmitter).first()
            if not tx_node:
                self.logger.error("While inserting messages: node '{}' does not exist.".format(transmitter))
                continue
            mm = Message(name = name, message_id = mid, dlc = dlc, sender = tx_node.rid)
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
                multiplexorSignal = None
                multiplexDependent = None
                multiplexorValue = None
                multiplexerIndicator = signal['multiplexerIndicator']
                if multiplexerIndicator:
                    match = CO_MPX.match(multiplexerIndicator)
                    if match:
                        gd = match.groupdict()
                        #print("MPX:", gd)
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
                self.session.add(ss)
                srid = ss.rid
                ms = Message_Signal(offset = startBit, multiplexor_signal = multiplexorSignal,
                    multiplex_dependent = multiplexDependent, multiplexor_value = multiplexorValue,
                    signal = ss, message = mm)
                self.session.add(ms)
                self.session.flush()
                self.insertReceivers(mm.rid, ss.rid, receiver)

    def exitMessage(self, ctx):
        ctx.value = dict(messageID = self.getValue(ctx.messageID), name = self.getValue(ctx.messageName),
            dlc = self.getValue(ctx.messageSize), transmitter = self.getTerminal(ctx.transmt),
            signals = [x.value for x in ctx.sgs]
        )

    def exitSignal(self, ctx):
        byteOrder = self.getValue(ctx.byteOrder)
        if not byteOrder in (0, 1):
            self.logger.error("While parsing signal: Error while parsing signal '{}': byteorder must be either 0 or 1 -- using 0".format(ctx.signalName.value))
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
        self.log_insertion("ValueTable")
        ctx.value = [x.value for x in ctx.items]
        for table in ctx.value:
            name = table['name']
            description = table['description']
            vt = Valuetable(name = name)
            self.session.add(vt)
            self.session.flush()
            self.log_insertion("\tValueDescription")
            self.insertValueDescription(vt.rid, description)
        self.session.flush()

    def exitValueTable(self, ctx):
        ctx.value = dict(name = ctx.name.value, description = [x.value for x in ctx.desc])

    def exitValueDescription(self, ctx):
        ctx.value = (ctx.name.value, ctx.val.value, )

    def exitNodes(self, ctx):
        self.log_insertion("Nodes")
        ctx.value = [x.value for x in ctx.ids]
        nodeSet = set(['Vector__XXX'])
        for name in ctx.value:
            if not name in nodeSet:
                nn = Node(name = name)
                self.session.add(nn)
            nodeSet.add(name)
        self.session.flush()

    def exitBitTiming(self, ctx):
        ctx.value = dict(baudrate = self.getValue(ctx.baudrate), btr1 = self.getValue(ctx.btr1), btr2 = self.getValue(ctx.btr2))

    def exitNewSymbols(self, ctx):
        ctx.value = [x.text for x in ctx.ids]

    def exitVersion(self, ctx):
        self.log_insertion("Version")
        ctx.value = self.getValue(ctx.vs)
        version = ctx.value
        network = self.network_id
        vers = Dbc_Version(version_string = version, network = network)
        self.session.add(vers)
        self.session.flush()

    def exitObjectValueTables(self, ctx):
        self.log_insertion("Object_Valuetable")
        ctx.value = [x.value for x in ctx.items]
        for table in ctx.value:
            tp = table['type']
            description = table['description']
            if tp == 'SG':
                object_rid = table['messageID']
                name = table['signalName']
                otype = 0
            elif tp == 'EV':
                name = table['envVarName']
                otype = 1
                env_var = self.ENVVAR_BY_NAME(self.session).params(name = name).first()
                if not env_var:
                    self.logger.error("While inserting object value tables: environment variable '{}' does not exist.".format(name))
                    continue
                object_rid = env_var.rid
            vt = Valuetable(name = name)
            self.session.add(vt)
            self.session.flush()
            ovt = Object_Valuetable(object_type= otype, object_rid = object_rid, valuetable_id = vt.rid)
            self.session.add(ovt)
            self.session.flush()
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
        self.log_insertion("EnvVar")
        # TODO: Process after EVDATA!!!
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
            env_data = self.ENVDATA_BY_NAME(self.session).params(name = name).first()
            if not env_data:
                #self.logger.error("Environment variable data '{}' does not exist.".format(name))
                #continue
                dataSize = 0
            else:
                dataSize = env_data.value
            envVar = EnvVar(name = name, type = varType, unit = unit, minimum = minimum, maximum = maximum,
                access = accessType, startup_value = initialValue, size = dataSize)
            self.session.add(envVar)
            for node in accessNodes:
                nn = self.NODE_BY_NAME(self.session).params(name = node).first()
                if not nn:
                    self.logger.error("While inserting environment variables: node '{}' does not exist.".format(name))
                    continue
                envVar.accessingNodes.append(nn)
        self.session.flush()

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
        self.log_insertion("EnvironmentVariablesData")
        ctx.value = [x.value for x in ctx.evars]
        for item in ctx.value:
            print("EVD", item)
            name = item['name']
            value = item['value']
            evd = EnvironmentVariablesData(name = name, value = value)
            self.session.add(evd)
        self.session.flush()

    def exitEnvironmentVariableData(self, ctx):
        ctx.value = dict(name = self.getValue(ctx.varname), value = self.getValue(ctx.value))

    def exitSignalTypes(self, ctx):
        self.log_insertion("Signal_Type")
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
        self.log_insertion("Comments")
        ctx.value = [x.value for x in ctx.items]
        for comment in ctx.value:
            tp = comment['type']
            text = comment['comment']
            key = comment['key']
            if tp == 'BU':
                obj = self.NODE_BY_NAME(self.session).params(name = key).first()
                if not obj:
                    self.logger.error("While inserting comments: node '{}' does not exist.".format(key))
                    continue
                obj.comment = text
            elif tp == 'BO':
                obj = self.MESSAGE_BY_MESSAGE_ID(self.session).params(message_id = key).first()
                if not obj:
                    self.logger.error("While inserting comments: message '{}' does not exist.".format(key))
                    continue
                obj.comment = text
            elif tp == 'SG':
                rid = self.get_signal_by_name(*key)
                if not rid:
                    self.logger.error("While inserting comments: message signal '{}' does not exist.".format(key))
                    continue
                obj = self.session.query(Signal).filter(Signal.rid == rid).first()
                obj.comment = text
            elif tp == 'EV':
                obj = self.ENVVAR_BY_NAME(self.session).params(name = key).first()
                if not obj:
                    self.logger.error("While inserting comments: environment variable '{}' does not exist.".format(key))
                    continue
                obj.comment = text
            else:   # NW !?
                obj = self.NETWORK_BY_RID(self.session).params(rid = self.network_id).first()
                if not obj:
                    self.logger.error("While inserting comments: network '{}' does not exist.".format(self.network_id))
                    continue
                obj.comment = text
        self.session.flush()

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
        self.log_insertion("AttributeValues")
        ctx.value = [x.value for x in ctx.items]
        values = []
        for attr in ctx.value:
            stringValue = None
            numValue = None
            value = attr['attributeValue']
            if isinstance(value, str):
                stringValue = value
            else:
                numValue = value
            aname = attr['name']
            ad = self.ATTRIBUTE_DEFINITION_BY_NAME(self.session).params(name = attr['name']).first()
            if not ad:
                self.logger.error("While inserting attribute values: attribute definition named '{}' does not exist.".format(attr['name']))
                continue
            attrType = self.getAttributeType(attr['attributeType'])
            if attrType == AttributeType.MESSAGE:
                key = attr['messageID']
                msg = self.MESSAGE_BY_MESSAGE_ID(self.session).params(message_id = key).first()
                if not msg:
                    self.logger.error("While inserting attribute values: message '{}' does not exist.".format(key))
                    continue
                rid = msg.rid
            elif attrType == AttributeType.SIGNAL:
                key = attr['messageID'], attr['signalName'],
                rid = self.get_signal_by_name(*key)
            elif attrType == AttributeType.NODE:
                key = attr['nodeName']
                node = self.NODE_BY_NAME(self.session).params(name = key).first()
                if not node:
                    self.logger.error("While inserting attribute values: node '{}' does not exist.".format(key))
                    continue
                rid = node.rid
            elif attrType == AttributeType.ENV_VAR:
                key = attr['envVarname']
                envvar = self.ENVVAR_BY_NAME(self.session).params(name = key).first()
                if not envvar:
                    self.logger.error("While inserting attribute values: environment variable '{}' does not exist.".format(key))
                    continue
                rid = envvar.rid
            elif attrType == AttributeType.NETWORK:
                key = ''
                rid = 0
            else:
                rid = 0
                key = ''
            exists = self.EXISTS_ATTRIBUTE_VALUE(self.session).params(rid = rid, ad = ad.rid).first()
            if exists:
                self.logger.error("While inserting attribute values: attribute value for {} {} {} already exists.".format(AttributeType.SIGNAL.name, key, ad.name))
            else:
                av = Attribute_Value(object_id = rid, attribute_definition = ad, num_value = numValue, string_value = stringValue)
                values.append(av)
        self.session.add_all(values)
        self.session.flush()

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
        self.log_insertion("RelativeAttributeValues")
        items = [x.value for x in ctx.items]
        ctx.value = items
        for attr in items:
            attributeName = attr['attributeName']
            attributeValue = attr['attributeValue']
            attrributeType = self.getAttributeType(attr['attributeType'])
            ad = self.ATTRIBUTE_DEFINITION_BY_NAME(self.session).params(name = attr['attributeName']).first()
            if not ad:
                self.logger.error("While inserting relative attribute values: attribute definition '{}' does not exist.".format(attr['attributeName']))
                continue
            node = self.NODE_BY_NAME(self.session).params(name = attr['nodeName']).first()
            if not ad:
                self.logger.error("While inserting relative attribute values: node '{}' does not exist.".format(attr['nodeName']))
                continue
            nodeId = node.rid
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
                if not rid:
                    self.logger.error("While inserting relative attribute values: message signal '{}'::'{}' does not exist".format(messageID, parent['signalName']))
                    continue
            elif attrributeType == AttributeType.REL_ENV_VAR:
                evName = parent['evName']
                env_var = self.ENVVAR_BY_NAME(self.session).params(name = evName).first()
                if not env_var:
                    self.logger.error("While inserting relative attribute values: environment variable '{}' does not exist.".format(evName))
                    continue
                rid = env_var.rid
                #optOid2 = ???
            elif attrributeType == AttributeType.REL_NODE:
                messageID = parent['messageID']
                optOid2 = messageID
                msg = self.MESSAGE_BY_MESSAGE_ID(self.session).params(message_id = messageID).first()
                if not msg:
                    self.logger.error("While inserting relative attribute values: message '{}' does not exist.".format(messageID))
                    continue
                rid = msg.rid
            arv = AttributeRel_Value(object_id = rid, attribute_definition = ad, num_value = numValue,
                string_value = stringValue, opt_object_id_1 = optOid1, opt_object_id_2 = optOid2
            )
            self.session.add(arv)
        self.session.flush()

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
        self.log_insertion("SignalGroups")
        items = [x.value for x in ctx.items]
        ctx.value = items
        for group in ctx.value:
            messageID = group['messageID']
            gValue = group['gvalue']
            signalNames = group['signals']
            groupName = group['groupName']
            msg = self.MESSAGE_BY_MESSAGE_ID(self.session).params(message_id = messageID).first()
            if not msg:
                self.logger.error("While inserting signal groups: message '{}' does not exist.".format(messageID))
                continue
            sg = Signal_Group(name = groupName, value = gValue, message = msg)
            self.session.add(sg)
            self.session.flush()
            for signalName in signalNames:
                signal = self.MESSAGE_SIGNAL_BY_NAME2(self.session).params(messageID = messageID, signalName = signalName).first()
                if not signal:
                    self.logger.error("While inserting signal groups: message signal '{}'::'{}' does not exist.".format(messageID, signalName))
                    continue
                sgs = Signal_Group_Signal(signal_group = sg, message = msg, signal = signal)
                self.session.add(sgs)
        self.session.flush()

    def exitSignalGroup(self, ctx):
        messageID = self.getValue(ctx.messageID)
        groupName = self.getValue(ctx.groupName)
        gvalue = self.getValue(ctx.gvalue)
        signals = [x.value for x in ctx.signals]
        ctx.value = dict(messageID = messageID, groupName = groupName, gvalue = gvalue, signals = signals)

    def exitCategoryDefinitions(self, ctx):
        self.log_insertion("Category_Definition")
        ctx.value = [x.value for x in ctx.items]
        for category in ctx.value:
            print("CAT-DEF", category)
            cd = Category_Definition(name = category['name'], key = category['category'], level = category['value'])
            self.session.add(cd)
        self.session.flush()

    def exitCategoryDefinition(self, ctx):
        ctx.value = dict(name = self.getValue(ctx.name), category = self.getValue(ctx.cat), value = self.getValue(ctx.num))

    def exitCategories(self, ctx):
        self.log_insertion("Categories")
        ctx.value = [x.value for x in ctx.items]
        for category in ctx.value:
            print("CAT-VALUE", category)
            attrType = category['type']
            catId = category['category']
            if attrType == 'BU':
                nodeName = category['nodeName']
                objType = CategoryType.NODE
                node = self.NODE_BY_NAME(self.session).params(node = nodeName).first()
                if not node:
                    self.logger.error("While inserting categories: node '{}' does not exist.".format(nodeName))
                    continue
                rid = node.rid
            elif attrType == 'BO':
                objType = CategoryType.MESSAGE
                messageID = category['messageID']
                msg = self.MESSAGE_BY_MESSAGE_ID(self.session).params(message_id = messageID).first()
                if not msg:
                    self.logger.error("While inserting categories: message '{}' does not exist.".format(messageID))
                    continue
                rid = msg.rid
            elif attrType == 'EV':
                envVarname = category['envVarname']
                objType = CategoryType.ENV_VAR
                env_var = self.ENVVAR_BY_NAME(self.session).params(name = envVarname)
                if not env_var:
                    self.logger.error("While inserting categories: environment variable '{}' does not exist.".format(envVarname))
                    continue
                rid = env_var.rid
            cv = Category_Value(object_id = rid, category_definition_id = catId, objecttype = objType)
            self.session.add(cv)
            print(cv)
        self.session.flush()

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
