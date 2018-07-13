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


from collections import OrderedDict
import re

from antlr4 import *

## Attributes
##  GenSigStartValue    ==> to set initial value until first message is received.
##  GenMsgCycleTime     ==> to set transmission rate

"""
Before moving on, note that J1939 is a bit special in regards to the CAN DBC file format:
- The ID is extended 29 bit - in DBC context, this means that the the leading bit of the ID is "flipped" and needs to be re-flipped
- Secondly, the relevant ID is the PGN, i.e. a sub part of the CAN ID (start bit 9, length 18)
"""

DIGITS = re.compile(r'(\d+)')

def validateMultiplexerIndicatior(value):
    if value == "M" or (value[0] == 'm' and value[1 : ].isdigit()):
        return True
    else:
        print("Invalid multiplex indicator: '{}'".format(value))
        return False


def extractAccessType(value):
    match = DIGITS.search(value)
    if match:
        return int(match.group())
    else:
        return None

class dbcListener(ParseTreeListener):


    def getList(self, attr):
        return [x for x in attr()] if attr() else []

    def getTerminal(self, attr):
        return attr().getText() if attr() else ''

    def exitDbcfile(self, ctx):
        self.value = OrderedDict(
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
            customAttributeDefinitions = ctx.customAttributeDefinitions().value,
            attributeDefaults = ctx.attributeDefaults().value,
            customAttributeDefaults = ctx.customAttributeDefaults().value,
            attributeValues = ctx.attributeValues().value,
            valueDescriptions = ctx.valueDescriptions().value,
            categoryDefinitions = ctx.categoryDefinitions().value,
            categories = ctx.categories().value,
            signalExtendedValueTypeList = ctx.signalExtendedValueTypeList().value
        )

    def exitMessageTransmitters(self, ctx):
        ctx.value = [x.value for x in ctx.items]

    def exitMessageTransmitter(self, ctx):
        transmitters = ctx.tx.value
        ctx.value = OrderedDict(messageID = ctx.messageID.value, transmitters = transmitters)

    def exitSignalExtendedValueTypeList(self, ctx):
        ctx.value = [x.value for x in ctx.items]

    def exitSignalExtendedValueType(self, ctx):
        messageID = ctx.messageID.value
        signalName = ctx.signalName.value
        valType = ctx.valType.value  # TODO: Validate ('0' | '1' | '2' | '3')
        ctx.value = OrderedDict(messageID = messageID, signalName = signalName, valueType = valType)

    def exitMessages(self, ctx):
        ctx.value = [x.value for x in ctx.items]

    def exitMessage(self, ctx):
        ctx.value = OrderedDict(messageID = ctx.messageID.value, name = ctx.messageName.value, dlc = ctx.messageSize.value,
            transmitter = ctx.transmt.text if ctx.transmt else None, signals = [x.value for x in ctx.sgs]
        )

    def exitSignal(self, ctx):
        ctx.value = OrderedDict(name = ctx.signalName.value, startBit = ctx.startBit.value, signalSize = ctx.signalSize.value,
            byteOrder = ctx.byteOrder.value, sign = -1 if ctx.sign.text == '-' else +1, factor = ctx.factor.value, offset = ctx.offset.value,
            minimum = ctx.minimum.value, maximum = ctx.maximum.value, unit = ctx.unit.value, receiver = ctx.rcv.value,
            multiplexerIndicator = ctx.mind.value if ctx.mind else None
        )

    def exitReceiver(self, ctx):
        ctx.value = [ctx.fid.text] + [x.value for x in ctx.ids]

    def exitTransmitter(self, ctx):
        ctx.value = [x.value for x in ctx.ids]

    def exitMultiplexerIndicator(self, ctx):
        mind = ctx.mind.value
        if validateMultiplexerIndicatior(mind):
            ctx.value = mind
        else:
             ctx.value = None

    def exitValueTables(self, ctx):
        ctx.value = [x.value for x in ctx.items]

    def exitValueTable(self, ctx):
        ctx.value = OrderedDict(name = ctx.name.value, description = [x.value for x in ctx.desc])

    def exitValueDescription(self, ctx):
        ctx.value = (ctx.name.value, ctx.val.value, )

    def exitNodes(self, ctx):
        ctx.value = [x.value for x in ctx.ids]

    def exitBitTiming(self, ctx):
        ctx.value = OrderedDict(baudrate = ctx.baudrate.value if ctx.baudrate else None,
            btr1 = ctx.btr1.value if ctx.btr1 else None,
            btr2 = ctx.btr2.value if ctx.btr2 else None
        )

    def exitNewSymbols(self, ctx):
        ctx.value = [x.text for x in ctx.ids]

    def exitVersion(self, ctx):
        ctx.value = ctx.vs.value

    def exitValueDescriptions(self, ctx):
        ctx.value = [x.value for x in ctx.items]

    def exitSpecializedValueDescription(self, ctx):
        items = [x.value for x in ctx.items]
        if ctx.messageID:
            messageID = ctx.messageID.value
            signalName = ctx.signalName.value
            di = OrderedDict(messageID = messageID, signalName = signalName)
            tp = "SG"
        else:
            envVarName = ctx.envVarName.value
            di = OrderedDict(envVarName = envVarName)
            tp = "EV"
        ctx.value = OrderedDict(type = tp, description = items, **di)

    def exitEnvironmentVariables(self, ctx):
        ctx.value = [x.value for x in ctx.evs]

    def exitEnvironmentVariable(self, ctx):
        accessType = extractAccessType(ctx.DUMMY_NODE_VECTOR().getText())

        ctx.value = OrderedDict(name = ctx.name.value, varType = ctx.varType.value, minimum = ctx.minimum.value,
            maximum = ctx.maximum.value, unit = ctx.unit.value, initialValue = ctx.initialValue.value, envId = ctx.envId.value,
            accessType = accessType, accessNodes = ctx.accNodes.value
        )

    def exitAccessNodes(self, ctx):
        nodes = [x.value for x in ctx.items]
        ctx.value = nodes

    def exitEnvironmentVariablesData(self, ctx):
        ctx.value = [x.value for x in ctx.evars]

    def exitEnvironmentVariableData(self, ctx):
        ctx.value = OrderedDict(name = ctx.varname.value, value = ctx.value.value)

    def exitSignalTypes(self, ctx):
        ctx.value =[x.value for x in ctx.sigTypes]

    def exitSignalType(self, ctx):
        ctx.value = OrderedDict(name = ctx.signalTypeName.value, size = ctx.signalSize.value, byteOrder = ctx.byteOrder.value,
            valueType = ctx.valueType.value, factor = ctx.factor.value, offset = ctx.offset.value, minimum = ctx.minimum.value,
            maximum = ctx.maximum.value, unit = ctx.unit.value, defaultValue = ctx.defaultValue.value, valTable = ctx.valTable.value,
        )

    def exitComments(self, ctx):
        ctx.value = [x.value for x in ctx.items]
        pass

    def exitComment(self, ctx):
        comment = ctx.s.value
        if ctx.c0:
            tp = "BU"
            key = ctx.c0.value
        elif ctx.i1:
            tp = "BO"
            key = ctx.i1.value
        elif ctx.i2:
            tp = "SG"
            key = (ctx.i2.value, ctx.c2.value, )
        elif ctx.c3:
            tp = "EV"
            key = ctx.c3.value
        else:
            tp = "GENERAL"
            key = None
        ctx.value = OrderedDict(type = tp, key = key, comment = comment)

    def exitAttributeDefinitions(self, ctx):
        ctx.value = [x.value for x in ctx.items]

    def exitAttributeDefinition(self, ctx):
        objectType = ctx.objectType.text if ctx.objectType else None
        attributeName = ctx.attrName.value
        attributeValue = ctx.attrValue.value
        ctx.value = OrderedDict(type = objectType, name = attributeName, value = attributeValue)

    def exitCustomAttributeDefinitions(self, ctx):
        ctx.value = [x.value for x in ctx.items]

    def exitCustomAttributeDefinition(self, ctx):
        objectType = ctx.objectType.text if ctx.objectType else None
        attributeName = ctx.attrName.value
        attributeValue = ctx.attrValue.value
        ctx.value = OrderedDict(type = objectType, name = attributeName, value = attributeValue)

    def exitAttributeValueType(self, ctx):
        if ctx.i00:
            tp = "INT"
            value = (ctx.i00.value, ctx.i01.value, )
        elif ctx.i10:
            tp = "INT"
            value = (ctx.i10.value, ctx.i11.value, )
        elif ctx.f0:
            tp = "FLOAT"
            value = (float(ctx.f0.value), float(ctx.f1.value), )
        elif ctx.s0:
            tp = "STRING"
            value = None
        elif ctx.efirst:
            tp = "ENUM"
            efirst = [ctx.efirst.value]
            eitems = [x.value for x in ctx.eitems]
            value = efirst + eitems
        ctx.value = OrderedDict(type = tp, value = value)

    def exitAttributeDefaults(self, ctx):
        defaults = {}
        for item in ctx.items:
            name, value = item.value
            defaults[name] = value
        ctx.value = defaults

    def exitAttributeDefault(self, ctx):
        name = ctx.n.value
        value = ctx.v.value
        ctx.value = (name, value)

    def exitCustomAttributeDefaults(self, ctx):
        defaults = {}
        for item in ctx.items:
            name, value = item.value
            defaults[name] = value
        ctx.value = defaults


    def exitCustomAttributeDefault(self, ctx):
        name = ctx.n.value
        value = ctx.v.value
        ctx.value = (name, value)

    def exitAttributeValue(self, ctx):
        if ctx.s:
            ctx.value = ctx.s.value
        elif ctx.n:
            ctx.value = ctx.n.value

    def exitAttributeValues(self, ctx):
        ctx.value = [x.value for x in ctx.items]

    def exitAttributeValueForObject(self, ctx):
        attributeName = ctx.attributeName.value
        if ctx.nodeName:
            nodeName = ctx.nodeName.value
            buValue = ctx.buValue.value
            di = OrderedDict(type = 'BU', nodeName = nodeName, value = buValue)
        elif ctx.mid1:
            mid1 = ctx.mid1.value
            boValue = ctx.boValue.value
            di = OrderedDict(type = 'BO', messageID = mid1, value = boValue)
        elif ctx.mid2:
            mid2 = ctx.mid2.value
            signalName = ctx.signalName.value
            sgValue = ctx.sgValue.value
            di = OrderedDict(type = 'SG', messageID = mid2, signalName = signalName, value = sgValue)
        elif ctx.evName:
            evName = ctx.evName.value
            evValue = ctx.evValue.value
            di = OrderedDict(type = 'EV', envVarname = evName, value = evValue)
        else:
            evValue = ctx.attrValue.value
            evName = None
            di = OrderedDict(type = "GENERAL", value = evValue)
        ctx.value = OrderedDict(name = attributeName, **di)

    def exitCategoryDefinitions(self, ctx):
        ctx.value = [x.value for x in ctx.items]

    def exitCategoryDefinition(self, ctx):
        ctx.value = OrderedDict(name = ctx.name.value, category = ctx.cat.value, value = ctx.num.value)

    def exitCategories(self, ctx):
        ctx.value = [x.value for x in ctx.items]

    def exitCategory(self, ctx):
        category = ctx.cat.value
        if ctx.nodeName:
            nodeName = ctx.nodeName.value
            di = OrderedDict(type = 'BU', nodeName = nodeName)
        elif ctx.mid1:
            mid1 = ctx.mid1.value
            di = OrderedDict(type = 'BO', messageID = mid1)
        elif ctx.mid2:
            mid2 = ctx.mid2.value
            signalName = ctx.signalName.value
            di = OrderedDict(type = 'SG', messageID = mid2, signalName = signalName)
        elif ctx.evName:
            evName = ctx.evName.value
            di = OrderedDict(type = 'EV', envVarname = evName)
        ctx.value = OrderedDict(category = category, **di)



    def exitIntValue(self, ctx):
        ctx.value = int(ctx.i.text) if ctx.i else None

    def exitFloatValue(self, ctx):
        ctx.value = float(ctx.f.text) if ctx.f else None

    def exitNumber(self, ctx):
        ctx.value = ctx.i.value if ctx.i else ctx.f.value

    def exitStringValue(self, ctx):
        ctx.value = ctx.s.text.strip('"') if ctx.s else None

    def exitIdentifierValue(self, ctx):
        ctx.value = ctx.i.text if ctx.i else None

