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


from functools import lru_cache

from pydbc.api.attribute import AttributeDefinition, AttributeValue, Value
from pydbc.api.limits import Limits
from pydbc.types import ValueType,AttributeType


class BaseObject:
    OBJECT_TYPE = None
    TABLE_NAME = None
    COLUMNS = ()
    KEY = None

    def __init__(self, database):
        self.database = database

    def update(self):
        attrValues = []
        for attr, _ in self.COLUMNS:
            attrValues.append(getattr(self, attr))
        cur = self.database.getCursor()
        where = "{} = {}".format(self.KEY, getattr(self, self.KEY))
        self.database.db.updateStatement(cur, self.TABLE_NAME, ','.join([c for a, c in self.COLUMNS]), where, attrValues)

    def remove(self):
        sql = "DELETE FROM {} WHERE {} = {}".format(self.TABLE_NAME, self.KEY, "?")
        cur = self.database.getCursor()
        key = [getattr(self, self.KEY)]
        cur.execute(sql, key)

    def setMultipleValues(self, **values):
        """
        """
        pass

    def applicableAttributes(self):
        """
        """
        if self.OBJECT_TYPE is not None:
            return self.database.applicableAttributes(self.OBJECT_TYPE)
        else:
            return None

    @property
    @lru_cache(maxsize = 1)
    def key(self):
        return getattr(self, self.KEY)

    def _attributeValue(self, oid, attr):   # TODO: factory.
        attrValue = self.database.attributeValue(oid, attr.rid)
        valueType = attr.valueType
        if attrValue:
            default = False
            if valueType in (ValueType.HEX, ValueType.INT, ValueType.FLOAT):
                value = attrValue['Num_Value']
            elif valueType == ValueType.STRING:
                value = attrValue['String_Value']
            elif valueType == ValueType.ENUM:
                enumValues = attr.enumValues
                idx = int(attrValue['Num_Value'])
                value = enumValues[idx]
        else:
            default = True
            value = attr.defaultValue
        return Value(value, default)

    def attribute(self, name):
        """
        """
        item = self.database.singleAttribute(self.OBJECT_TYPE, name)
        if item:
            attr = AttributeDefinition.create(self.database, item)
            value = self._attributeValue(self.key, attr)
            return AttributeValue(self.database.db, self.key, attr, value)
        else:
            return None # TODO: execption!

    @property
    def attributes(self):
        """
        """
        for item in self.applicableAttributes():
            attr = AttributeDefinition.create(self.database, item)
            value = self._attributeValue(self.key, attr)
            yield AttributeValue(self.database.db, self.key, attr, value)

    def __str__(self):
        result = []
        attrs = []
        result.append("{}(".format(self.__class__.__name__))
        for attr, column in self.COLUMNS:
            value = getattr(self, attr)
            if attr == 'comment' and value is None:
                value = ""
            fmt = "{} = '{}'" if isinstance(value, str) else "{} = {}"
            attrs.append(fmt.format(attr, value))
        result.append(', '.join(attrs))
        result.append(")")
        return ''.join(result)

    __repr__ = __str__

    def reload(self):
        """
        Reload after rollback.
        """
        pass

