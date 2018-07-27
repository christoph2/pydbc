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

from pydbc.types import CANAddress, AttributeType, ValueType
from pydbc.api.limits import Limits
from pydbc.logger import Logger


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
            self.defaultValue = attr['Default_Number']
        elif self.valueType in (ValueType.STRING, ValueType.ENUM):
            self.defaultValue = attr['Default_String']

        #self.defaultNumber = attr['Default_Number']
        #self.defaultString = attr['Default_String']

    def __str__(self):
        comment = '' if self.comment is None else self.comment
        return "{}(name = '{}', objectType = {}, valueType = {}, limits = {}, default = {}, values = {}, comment = '{}')".format(
            self.__class__.__name__, self.name, self.objectType.name, self.valueType.name, self.limits, self.defaultValue,
            self.enumValues, comment
        )

    __repr__ = __str__


class Value:
    """
    """

    __slots__ = ['parent', '_value', '_default']

    def __init__(self, value, default):
        self._value = value
        self._default = default

    def _convertValue(self):
        valueType = self.attr.valueType
        if valueType in (ValueType.HEX, ValueType.INT):
            self._value = int(self._value)
        elif valueType == ValueType.FLOAT:
            self._value = float(self._value)
        elif valueType == ValueType.STRING:
            self._value = str(self._value)
        elif valueType == ValueType.ENUM:
            self._value = str(self._value)

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

    def _rangeCheck(self, value):
        vt = self.attr.valueType
        if vt in (ValueType.INT, ValueType.HEX, ValueType.FLOAT):
            if self.limits.min is not None:
                if value < self.limits.min:
                    raise ValueError("Value lesser than minimum")
            if self.limits.max is not None:
                if value > self.limits.min:
                    raise ValueError("Value greater than maximum")
        elif vt == ValueType.ENUM:
            enumValues = self.attr.enumValues
            if not value in self.attr.enumValues:
                raise ValueError("Invalid enumerator '{}'".format(value))

    def _setValue(self, value):
        print("Setting value", value)
        self._typeCheck(value)
        self._rangeCheck(value)
        self._value = value
        self._default = False

    def _getValue(self):
        return self._value

    def update(self):
        value = self.fetchValue()
        valueType = self.attr.valueType
        cur = self.db.getCursor()
        print("UPDATE:", self.objectID, self.attr.rid, value, self.attr.defaultValue, self.attr.valueType.name)
        if valueType == ValueType.STRING:
            self.db.replaceStatement(cur, "Attribute_Value", "Object_ID, Attribute_Definition, String_Value", self.objectID, self.attr.rid, self.value)
        elif valueType == ValueType.ENUM:
            idx = enumValues.index(self.value)
            self.db.replaceStatement(cur, "Attribute_Value", "Object_ID, Attribute_Definition, Num_Value", self.objectID, self.attr.rid, idx)
        else:
            self.db.replaceStatement(cur, "Attribute_Value", "Object_ID, Attribute_Definition, Num_Value", self.objectID, self.attr.rid, self.value)

    def reset(self):
        """
        """
        cur = self.db.getCursor()
        cur.excute("DELETE FROM attribute_value WHERE object_id = ? AND Attribute_Definition = ?", [self.objectID, self.attr.rid])
        self._value = self.defaultValue
        self._default = True

    def fetchValue(self):
        return self.db.fetchSingleRow("Attribute_Value", column = "*", where = "Object_ID = {} AND Attribute_Definition = {}".format(
            self.objectID, self.attr.rid)
        )

    value = property(_getValue, _setValue)

    @property
    def db(self):
        return self.parent.db

    @property
    def attr(self):
        return self.parent.attr

    @property
    def objectID(self):
        return self.parent.objectID

    @property
    def defaultValue(self):
        return self.parent.defaultValue

    @property
    def limits(self):
        return self.parent.limits

    @property
    def default(self):
        return self._default

    def __str__(self):
        value = "'{}'".format(self._value) if self.attr.valueType in (ValueType.STRING, ValueType.ENUM) else self.value
        return "Value({1}: {0} [default = {2}])".format(value, self.attr.valueType.name, self.default)

    __repr__ = __str__


class AttributeValue:
    """
    """

    __slots__ = ['db', '_value', 'attr', '_objectID']

    def __init__(self, db, objectID, attr, value):
        self.db = db
        self.attr = attr
        self._value = value
        self._value.parent = self
        self._value._convertValue()
        self._objectID = objectID

    def update(self):
        self._value.update()

    def reset(self):
        """Reset attribute value to default.
        """
        self._value.reset()

    def _setValue(self, value):
        self._value.value = value

    def _getValue(self):
        return self._value.value

    @property
    def objectID(self):
        return self._objectID

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

