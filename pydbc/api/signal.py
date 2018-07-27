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


from pydbc.types import AttributeType, MultiplexingType
from pydbc.api.base import BaseObject
from pydbc.api.limits import Limits


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

    def __init__(self, database, messageId, rid, name, startBit, bitSize, byteOrder, valueType, formula,
                 limits, unit, multiplexing, comment):
        super(Signal, self).__init__(database)
        self.messageid = messageId
        self.rid = rid
        self.name = name
        self.startBit = startBit
        self.bitSize = bitSize
        self.byteOrder = byteOrder
        self.valueType = valueType
        self.formula = formula
        self.multiplexing = multiplexing
        self.comment = comment
        self.limits = limits
        self.unit = unit

    def values(self):
        pass

    def valuesFromGlobalTable(self):
        pass

    def __str__(self):
        return '{}(name = "{}", type = {}, startBit = {}, bitSize = {}, byteOrder = {}, unit = "{}",\
 limits = {}, formula = {}, multiplexing = {}, comment = "{}")'.format(self.__class__.__name__, self.name,
            self.valueType.name, self.startBit, self.bitSize, self.byteOrder.name, self.unit, self.limits,
            self.formula, self.multiplexing, self.comment or ""
        )

    #__repr__ = __str__

