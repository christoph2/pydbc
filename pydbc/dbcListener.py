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

from antlr4 import *

## Attributes
##  GenSigStartValue    ==> to set initial value until first message is received.
##  GenMsgCycleTime     ==> to set transmission rate

def validateMultiplexerIndicatior(value):
    if value == "M" or (value[0] == 'm' and value[1 : ].isdigit()):
        return True
    else:
        print("Invalid multiplex indicator: '{}'".format(value))
        return False


class dbcListener(ParseTreeListener):


    def getList(self, attr):
        return [x for x in attr()] if attr() else []

    def getTerminal(self, attr):
        return attr().getText() if attr() else ''

    def getInt(self, attr):
        return int(attr.text) if attr else None

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
            attributeDefaults = ctx.attributeDefaults().value,
            attributeValues =ctx.attributeValues().value,
            valueDescriptions = ctx.valueDescriptions().value,
            signalExtendedValueTypeList = ctx.signalExtendedValueTypeList().value
        )

    def exitMessageTransmitters(self, ctx):
        ctx.value = [x.value for x in ctx.items]

    def exitMessageTransmitter(self, ctx):
        print("MTX:", self.getInt(ctx.messageID), ctx.transmitter.value)
        ctx.value = OrderedDict(messageID = self.getInt(ctx.messageID), transmitter = ctx.transmitter.value)

    def exitSignalExtendedValueTypeList(self, ctx):
        messageID = int(ctx.messageID.text) if ctx.messageID else None
        signalName = ctx.signalName.value if ctx.signalName else None
        valType = int(ctx.valType.text) if ctx.valType else None  # TODO: Validate ('0' | '1' | '2' | '3')
        print("SIG_VALTYPE:", messageID, signalName, valType)
        ctx.value = OrderedDict(messageID = messageID, signalName = signalName, valueType = valType)

    def exitMessages(self, ctx):
        ctx.value = [x.value for x in ctx.items]

    def exitMessage(self, ctx):
        print("MSG:", self.getInt(ctx.messageID), ctx.messageName.text, self.getInt(ctx.messageSize), ctx.transmt.text, )
        ctx.value = OrderedDict(messageID = self.getInt(ctx.messageID), name = ctx.messageName.text, dlc = self.getInt(ctx.messageSize),
            transmitter = ctx.transmt.text, signals = [x.value for x in ctx.sgs]
        )

    def exitSignal(self, ctx):
        print("    SIG:", ctx.signalName.text, self.getInt(ctx.startBit), self.getInt(ctx.signalSize), ctx.byteOrder.text, ctx.valueType.text,
            ctx.factor.value, ctx.offset.value, ctx.minimum.value, ctx.maximum.value, ctx.unit.text, ctx.rcv.value)

        ctx.value = OrderedDict(name = ctx.signalName.text, startBit = self.getInt(ctx.startBit), signalSize = self.getInt(ctx.signalSize),
            byteOrder = ctx.byteOrder.text, valueType = ctx.valueType.text, factor = ctx.factor.value, offset = ctx.offset.value,
            minimum = ctx.minimum.value, maximum = ctx.maximum.value, unit = ctx.unit.text, receiver = ctx.rcv.value,
            multiplexerIndicator = ctx.mind.value if ctx.mind else None
        )

    def exitReceiver(self, ctx):
        ctx.value = [ctx.fid.text] + [x.text for x in ctx.ids]

    def exitTransmitter(self, ctx):
        ctx.value = [ctx.fid.text] + [x.text for x in ctx.ids]

    def exitMultiplexerIndicator(self, ctx):
        mind = ctx.mind.text
        if validateMultiplexerIndicatior(mind):
            ctx.value = mind
        else:
             ctx.value = None

    def exitValueTables(self, ctx):
        print("VTs:", [x.value for x in self.getList(ctx.valueTable)])
        ctx.value = [x.value for x in self.getList(ctx.valueTable)]

    def exitValueTable(self, ctx):
        ctx.value = OrderedDict(name = ctx.name.text, description = [x.value for x in ctx.desc])

    def exitValueDescription(self, ctx):
        ctx.value = (ctx.name.text, ctx.val.value, )

    def exitNodes(self, ctx):
        ctx.value = [x.text for x in ctx.ids]

    def exitBitTiming(self, ctx):
        ctx.value = OrderedDict(baudrate = self.getInt(ctx.baudrate),
            btr1 = self.getInt(ctx.btr1), btr2 = self.getInt(ctx.btr2)
        )

    def exitNewSymbols(self, ctx):
        ctx.value = [x.text for x in ctx.ids]

    def exitVersion(self, ctx):
        ctx.value = self.getTerminal(ctx.STRING)

    def exitValueDescriptions(self, ctx):
        ctx.value = OrderedDict(signals = [x.value for x in ctx.vds], envVars = [x.value for x in ctx.vde])

    def exitValueDescriptionForSignal(self, ctx):
        ctx.value = OrderedDict(messageID = self.getInt(ctx.messageID), signalName = ctx.signalName.text, valueDescription = [x.value for x in ctx.vds])

    def exitValueDescriptionsForEnvVar(self, ctx):
        ctx.value = OrderedDict(signalName = self.getInt(ctx.signalName), valueDescription = [x.value for x in ctx.vds])


    def exitEnvironmentVariables(self, ctx):
        print("EVS: ", [x.value for x in ctx.evs])
        ctx.value = [x.value for x in ctx.evs]

    def exitEnvironmentVariable(self, ctx):
        ctx.value = OrderedDict(name = ctx.name.text, varType = self.getInt(ctx.varType), minimum = ctx.minimum.value,
            maximum = ctx.maximum.value, unit = ctx.unit.text, initialValue = ctx.initialValue.value, envId = self.getInt(ctx.envId),
            dnv = ctx.DUMMY_NODE_VECTOR().getText(), accessNodes = ctx.accNodes.value
        )

    def exitAccessNodes(self, ctx):
        ctx.value = OrderedDict(id = ctx.id_.text if ctx.id_ else None, ids = ctx.ids)

    def exitEnvironmentVariablesData(self, ctx):
        ctx.value = [x.value for x in ctx.evars]

    def exitEnvironmentVariableData(self, ctx):
        ctx.value = (ctx.varname.text, self.getInt(ctx.value))

    def exitSignalTypes(self, ctx):
        print("SIGTYPES:", [x.value for x in ctx.sigTypes])
        ctx.value =[x.value for x in ctx.sigTypes]

    def exitSignalType(self, ctx):
        ctx.value = OrderedDict(name = ctx.signalTypeName.text, size = ctx.signalSize.value, byteOrder = self.getInt(ctx.byteOrder),
            valueType = ctx.valueType.text, factor = ctx.factor.value, offset = ctx.offset.value, minimum = ctx.minimum.value,
            maximum = ctx.maximum.value, unit = ctx.unit.text, defaultValue = ctx.defaultValue.value, valTable = ctx.valTable.text,
        )

    def exitComments(self, ctx):
        print("COMMENTS:", [x.value for x in ctx.items])
        ctx.value = [x.value for x in ctx.items]
        pass

    def exitComment(self, ctx):
        comment = ctx.s.text
        if ctx.c0:
            tp = "BU"
            key = ctx.c0.text
        elif ctx.i1:
            tp = "BO"
            key = int(ctx.i1.text)
        elif ctx.i2:
            tp = "SG"
            key = (int(ctx.i2.text), ctx.c2.text, )
        elif ctx.c3:
            tp = "EV"
            key = ctx.c3.text
        ctx.value = OrderedDict(type = tp, key = key, comment = comment)

    def exitAttributeDefinitions(self, ctx):
        ctx.value = [x.value for x in ctx.items]

    def exitAttributeDefinition(self, ctx):
        objectType = ctx.objectType.text if ctx.objectType else None
        attributeName = ctx.attributeName.text
        attributeValue = ctx.attributeValue.value
        ctx.value = OrderedDict(type = objectType, name = attrName, value = attrValue)

    def exitAttributeValueType(self, ctx):
        if ctx.i00:
            tp = "INT"
            value = (int(ctx.i00.text), int(ctx.i01.text), )
        elif ctx.i10:
            tp = "INT"
            value = (int(ctx.i10.text, 16), int(ctx.i11.text, 16), )
        elif ctx.f0:
            tp = "FLOAT"
            value = (float(ctx.f0.text), float(ctx.f1.text), )
        elif ctx.s0:
            tp = "STRING"
            value = None
        elif ctx.efirst:
            tp = "ENUM"
            efirst = [ctx.efirst.text]
            eitems = [x.text for x in ctx.eitems]
            value = efirst + eitems
        ctx.value = OrderedDict(type = tp, value = value)

    def exitAttributeDefaults(self, ctx):
        ctx.value = [x.value for x in ctx.items]

    def exitAttributeDefault(self, ctx):
        name = ctx.n.text
        value = ctx.v.value
        print("DEFAULT:", name, value)
        ctx.value = OrderedDict(name = name, value = value)

    def exitAttributeValue(self, ctx):
        text = ctx.STRING()
        number = ctx.number()
        if text:
            ctx.value = text
        else:
            ctx.value = number

    def exitAttributeValues(self, ctx):
        ctx.value = [x.value for x in ctx.items]

    def exitAttributeValueForObject(self, ctx):
        attributeName = ctx.attributeName.text
        if ctx.nodeName:
            nodeName = ctx.nodeName.text
            buValue = ctx.buValue.value
            di = OrderedDict(type = 'BU', nodeName = nodeName, value = buValue)
        elif ctx.mid1:
            mid1 = self.getInt(ctx.mid1)
            boValue = ctx.boValue.value
            di = OrderedDict(type = 'BO', messageID = mid1, value = boValue)
        elif ctx.mid2:
            mid2 = self.getInt(ctx.mid2)
            signalName = ctx.signalName.text
            sgValue = ctx.sgValue.value
            di = OrderedDict(type = 'SG', messageID = mid2, signalName = signalName, value = sgValue)
        elif ctx.evName:
            evName = ctx.evName.text
            evValue = ctx.evValue.value
            di = OrderedDict(type = 'EV', envVarname = evName, value = evValue)
        ctx.value = OrderedDict(name = attributeName, **di)

    def exitNumber(self, ctx):
        ctx.value = int(ctx.INT().getText()) if ctx.INT() else  float(ctx.FLOAT().getText())

