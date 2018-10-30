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


from pydbc.types import AttributeType, MultiplexingType, ValueTableType, ByteOrderType, SignalType
from pydbc.api.base import BaseObject
from pydbc.api.limits import Limits
from pydbc.api.valuetable import ValueTable #, Value

class Multiplexing:
    """
    """

    def __init__(self, type = None, value = None):
        self.type =  MultiplexingType(type) or MultiplexingType(0)
        self.value = value

    def __str__(self):
        if self.type == MultiplexingType.DEPENDENT:
            result = "Depends on multiplexor-value {}".format(self.value)
        else:
            result = "type: {}".format(self.type.name)
        return "{}({})".format(self.__class__.__name__, result)

    __repr__ = __str__


class Formula:
    """
    """

    def __init__(self, factor = 1.0, offset = 0.0):
        self.factor = float(factor)
        self.offset = float(offset)

    def __str__(self):
        return "{}(factor = {}, offset = {})".format(self.__class__.__name__, self.factor, self.offset)

    __repr__ = __str__


class Signal(BaseObject):
    """
    """

    OBJECT_TYPE = AttributeType.SIGNAL
    TABLE_NAME = "Signal"

    KEY = 'rid'
    COLUMNS = (
        ('name', 'Name'),
        ('comment', 'Comment'),
        ('bitSize', 'Bitsize'),
        ('byteOrder', 'Byteorder'),
        ('valueType', 'Valuetype'),
        ('unit', 'Unit'),
    )

    def __init__(self, database, mrid, signal):
        super(Signal, self).__init__(database)
        self.messageid = mrid
        self.rid = signal['RID']
        self.name = signal['Name']

        messageSignal = self.database.messageSignal(mrid, self.rid)
        mpx = self.getMultiplexing(messageSignal)

        self.startBit = messageSignal['Offset']
        self.bitSize = signal['Bitsize']
        self.byteOrder = ByteOrderType(signal['Byteorder'])

        valueType = SignalType(signal['Valuetype'])
        sign = signal['Sign']
        if valueType == SignalType.SINT and sign == +1:
            valueType = SignalType.UINT
        self.valueType = valueType
        self.formula = Formula(signal['Formula_Factor'], signal['Formula_Offset'])
        self.multiplexing = mpx if mpx.type != MultiplexingType.NONE else None
        self.comment = signal['Comment']
        self.limits = Limits(signal['Minimum'], signal['Maximum'])
        self.unit = signal['Unit']
        self.valueTable = ValueTable(self.database, ValueTableType.SIGNAL, self.rid)

    def getMultiplexing(self, messageSignal):   # TODO: property multiplexing
        """
        """
        mpxValue = messageSignal['Multiplexor_Value']
        mpxDependent = messageSignal['Multiplex_Dependent']
        mpxSignal = messageSignal['Multiplexor_Signal']
        if mpxSignal == 1:
            mpxType = MultiplexingType.MULTIPLEXOR
        elif mpxDependent == 1:
            mpxType = MultiplexingType.DEPENDENT
        else:
            mpxType = MultiplexingType.NONE
        return Multiplexing(mpxType, mpxValue)

    @property
    def values(self):
        """
        """
        return self.valueTable

    @values.setter
    def values(self, vs):
        """
        """
        pass

    @property
    def valuetable(self):
        pass

    def valuesFromGlobalTable(self):
        """
        """
        pass

    def __str__(self):
        return '{}(name = "{}", type = {}, startBit = {}, bitSize = {}, byteOrder = {}, unit = "{}",\
 limits = {}, formula = {}, multiplexing = {}, values = {}, comment = "{}")'.format(self.__class__.__name__, self.name,
            self.valueType.name, self.startBit, self.bitSize, self.byteOrder.name, self.unit, self.limits,
            self.formula, self.multiplexing, self.valueTable.values or [], self.comment or ""
        )

    __repr__ = __str__

