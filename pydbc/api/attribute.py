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

import enum
import sys
import os

from pydbc.types import AttributeType, ValueType
from pydbc.db.types import CANAddress
from pydbc.db.creator import Creator
from pydbc.db import CanDatabase
from pydbc.logger import Logger


class Limits:

    def __init__(self, min, max):
        self.typeCheck(min)
        self.typeCheck(max)
        if not (min is None and max is None) and max < min:
            raise ValueError("max is smaller than min.")
        self._min = min
        self._max = max

    def getMin(self):
        return self._min

    def setMin(self, value):
        self.typeCheck(value)
        if not (value is None and self.max is None) and self.max < value:
            raise ValueError("min is larger than max.")
        self._min = value

    def getMax(self):
        return self._max

    def setMax(self, value):
        self.typeCheck(value)
        if not (self.min is None and value is None) and value < self.min:
            raise ValueError("max is smaller than min.")
        self._max = value

    def typeCheck(self, value):
        if not (isinstance(value, (int, float)) or value is None):
            raise TypeError("Value needs to be int, float, or None.")

    min = property(getMin, setMin)
    max = property(getMax, setMax)

    def __str__(self):
        minimum = "N/A" if self.min is None else self.min
        maximum = "N/A" if self.max is None else self.max
        return "{}(min = {}, max = {})".format(self.__class__.__name__, minimum, maximum)

    __repr__ = __str__


class AttributeDefinition:

    def __init__(self, attr):
        self.valueType = ValueType(attr['Valuetype'])
        self.name = attr['Name']
        self.comment = attr['Comment']
        self.objectType = AttributeType(attr['Objecttype'])
        self.rid = attr['RID']
        self.limits = Limits(attr['Minimum'], attr['Maximum'])
        self.enumValues = [ev for ev in attr['Enumvalues'].split(";")] if attr['Enumvalues'] else []

        if self.valueType in (ValueType.HEX, ValueType.INT, ValueType.FLOAT):
            self.default = attr['Default_Number']
        elif self.valueType in (ValueType.STRING, ValueType.ENUM):
            self.default = attr['Default_String']

        self.defaultNumber = attr['Default_Number']
        self.defaultString = attr['Default_String']

    def __str__(self):
        comment = '' if self.comment is None else self.comment
        return "{}(name = '{}', objectType = {}, valueType = {}, limits = {}, default = {}, values = {}, comment = '{}')".format(
            self.__class__.__name__, self.name, self.objectType.name, self.valueType.name, self.limits, self.default,
            self.enumValues, comment
        )

    __repr__ = __str__


class Value:
    """
    """

    __slots__ = ['attr', 'objectID', '_value', 'default']

    def __init__(self, objectID, attr, value, default):
        if attr.valueType in (ValueType.HEX, ValueType.INT):
            self._value = int(value)
        elif attr.valueType == ValueType.FLOAT:
            self._value = float(value)
        elif attr.valueType == ValueType.STRING:
            self._value = str(value)
        elif attr.valueType == ValueType.ENUM:
            self._value = str(value)
        else:
            self._value = value
        self.objectID = objectID
        self.attr = attr
        self.default = default

    def _typeCheck(self, value):
        vt = self.attr.valueType
        if vt in (ValueType.INT, ValueType.HEX):
            if not isinstance(value, int):
                raise TypeError("Value must be of type 'int'")
        elif vt == ValueType.FLOAT:
            if not isinstance(value, float):
                raise TypeError("Value must be of type 'float'")
        elif vt == ValueType.STRING:
            if not isinstance(value, str):
                raise TypeError("Value must be of type 'str'")
        elif vt == ValueType.ENUM:
            if not isinstance(value, str):
                raise TypeError("Value must be of type 'str'")
        self._value = value

    def _rangeCheck(self, value):
        vt = self.attr.valueType
        if vt in (ValueType.INT, ValueType.HEX, ValueType.FLOAT):
            pass    # check limits.
        elif vt == ValueType.ENUM:
            enumValues = self.attr.enumValues
            if not value in self.attr.enumValues:
                raise ValueError("Invalid enumerator '{}'".format(value))
            index = enumValues.index(value)

    def _setValue(self, value):
        print("Setting value", value)
        self._typeCheck(value)
        self._rangeCheck(value)

    def _getValue(self):
        return self._value

    value = property(_getValue, _setValue)

    def __str__(self):
        value = "'{}'".format(self._value) if self.attr.valueType in (ValueType.STRING, ValueType.ENUM) else self.value
        return "Value({1}: {0} [default = {2}])".format(value, self.attr.valueType.name, self.default)

    __repr__ = __str__


class AttributeValue:
    """
    """

    __slots__ = ['_value', 'attr']

    def __init__(self, attr, value):
        self.attr = attr
        self._value = value

    def update(self):
        pass

    def reset(self):
        """Reset attribute value to default.
        """
        pass

    def _setValue(self, value):
        self._value.value = value

    def _getValue(self):
        return self._value.value

    @property
    def name(self):
        return self.attr.name

    @property
    def valueType(self):
        return self.attr.valueType

    @property
    def comment(self):
        return self.attr.comment

    @property
    def objectType(self):
        return self.attr.objectType

    @property
    def rid(self):
        return self.attr.rid

    @property
    def limits(self):
        return self.attr.limits

    value = property(_getValue, _setValue)

    def __str__(self):
        return "{}('{}', {})".format(self.__class__.__name__, self.attr.name, self._value)

    __repr__ = __str__

