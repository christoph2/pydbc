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


DBC_EXTENSION = "dbc"
DB_EXTENSION = "vndb"


class DuplicateRecordError(Exception): pass


class Value:
    """
    """

    __slots__ = ['attr', '_value', 'default']

    def __init__(self, attr, value, default):
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
        #if :
        pass

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


class BaseObject:
    OBJECT_TYPE = None
    TABLE_NAME = None
    COLUMNS = ()
    KEY = None

    def __init__(self, database):
        self.database = database

    def update(self):
        attrValues = []
        columns = []
        for attr, column in self.COLUMNS:
            attrValues.append(getattr(self, attr))
            columns.append("{} = ?".format(column))
        attrValues.append(getattr(self, self.KEY))
        sqlColumns = ', '.join(columns)
        sql = "UPDATE OR FAIL {} SET {} WHERE {} = {}".format(self.TABLE_NAME, sqlColumns, self.KEY, "?")
        print("Updating {}... ==> {} :: {}".format(self.__class__.__name__, sql, attrValues))
        cur = self.database.getCursor()
        cur.execute(sql, attrValues)

    def remove(self):
        sql = "DELETE FROM {} WHERE {} = {}".format(self.TABLE_NAME, self.KEY, "?")
        cur = self.database.getCursor()
        key = getattr(self, self.KEY)
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

    #@Cached
    def getKey(self):
        key = getattr(self, self.KEY)
        return key

    def attribute(self, name):
        """
        """

        value = Value(self, value, default)
        return AttributeValue(objectType, rid, name, value, comment)

    def _attributeValue(self, oid, attr, valueType):
        attrValue = self.database.attributeValue(oid, attr.rid)
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
            value = attr.default
            #if valueType in (ValueType.HEX, ValueType.INT, ValueType.FLOAT):
            #    value = attr.defaultNumber
            #elif valueType in (ValueType.STRING, ValueType.ENUM):
            #    value = attr.defaultString
        return Value(attr, value, default)

    @property
    def attributes(self):
        """
        """
        for item in self.applicableAttributes():
            attr = AttributeDefinition(item)
            valueType = attr.valueType
            name = attr.name
            comment = attr.comment
            objectType = attr.objectType
            rid = attr.rid
            limits = attr.limits
            value = self._attributeValue(self.getKey(), attr, valueType)
            yield AttributeValue(objectType, rid, name, value, comment)

    def lastInsertedRowId(self, cur):
        return self.database.db.lastInsertedRowId(cur)

    def __str__(self):
        result = []
        attrs = []
        result.append("{}(".format(self.__class__.__name__))
        for attr, column in self.COLUMNS:
            value = getattr(self, attr)
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

class AttributeValue:

    def __init__(self, objectType, rid, name, value, comment):
        self.objectType = objectType
        self.rid = rid
        self.name = name
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

    value = property(_getValue, _setValue)

    def __str__(self):
        return "{}('{}', {})".format(self.__class__.__name__, self.name, self._value)

    __repr__ = __str__


class Limits:

    def __init__(self, min, max):
        self._min = min
        self._max = max

    def getMin(self):
        return self._min

    def setMin(self, value):
        self._min = value

    def getMax(self):
        return self._max

    def setMax(self, value):
        self._max = value

    min = property(getMin, setMin)
    max = property(getMax, setMax)

    def __str__(self):
        minimum = "N/A" if self.min is None else self.min
        maximum = "N/A" if self.max is None else self.max
        return "{}(min = {}, max = {})".format(self.__class__.__name__, minimum, maximum)

    __repr__ = __str__


class Node(BaseObject):
    """
    """

    OBJECT_TYPE = AttributeType.NODE
    TABLE_NAME = "Node"

    KEY = 'rid'
    COLUMNS = (
        ('name', 'Name'),
        ('comment', 'Comment'),
    )

    def __init__(self, database, rid, name, comment):
        super(Node, self).__init__(database)
        self.rid = rid
        self.name = name
        self.comment = comment


class Message(BaseObject):
    """
    CREATE TABLE IF NOT EXISTS Message (
        RID INTEGER NOT NULL DEFAULT 0,
        Name VARCHAR(255) NOT NULL,
        Message_ID INTEGER NOT NULL DEFAULT 0,
        Message_Format INTEGER NOT NULL DEFAULT 0,
        DLC INTEGER DEFAULT 0,
        Transmission_Type INTEGER DEFAULT 0,
        Cycletime INTEGER DEFAULT 0,
        Sender INTEGER DEFAULT 0,
        "Comment" VARCHAR(255),
        PRIMARY KEY(RID),
        UNIQUE(Name),
        UNIQUE(Message_ID)
    );
    """

    OBJECT_TYPE = AttributeType.MESSAGE
    TABLE_NAME = "Message"

    KEY = 'rid'
    COLUMNS = (
        ('name', 'Name'),
        ('identifier', 'Message_ID'),
        ('dlc', 'DLC'),
        ('sender', 'Sender'),
        ('comment', 'Comment'),
    )

    def __init__(self, database, rid, name, identifier, dlc, sender, comment):
        super(Message, self).__init__(database)
        self.rid = rid
        self.name = name
        self.identifier = identifier
        self.dlc = dlc
        self.sender = sender
        self.comment = comment


class Signal(BaseObject):
    """
        RID INTEGER NOT NULL DEFAULT 0,
        Name VARCHAR(255) NOT NULL,
        Bitsize INTEGER DEFAULT 0,
        Byteorder INTEGER DEFAULT 0,
        Valuetype INTEGER DEFAULT 0,
        Initialvalue FLOAT8 DEFAULT 0,
        Formula_Factor FLOAT8 DEFAULT 1,
        Formula_Offset FLOAT8 DEFAULT 0,
        Minimum FLOAT8 DEFAULT 0,
        Maximum FLOAT8 DEFAULT 0,
        Unit VARCHAR(255),
        "Comment" VARCHAR(255),
    """

    OBJECT_TYPE = AttributeType.SIGNAL
    TABLE_NAME = "Signal"

    KEY = 'rid'
    COLUMNS = (
        ('name', 'Name'),
        ('comment', 'Comment'),
    )

    def __init__(self, database, rid, name, comment):
        super(Signal, self).__init__(database)
        self.rid = rid
        self.name = name
        self.comment = comment

    def values(self):
        pass

    def valuesFromGlobalTable(self):
        pass


class Database:

    """
    """
    def __init__(self, dbname, dbtype = "CAN", template = None, inMemory = False, logLevel = 'INFO'):
        """
        """
        self.logger = Logger("api.database", level = logLevel)
        dbname = "{}.{}".format(dbname, DB_EXTENSION)
        self.dbname = dbname if not inMemory else ":memory:"
        self.logger.info("Initializing Sqlite3 database '{}'".format(self.dbname))
        self.dbtype = dbtype    # TODO: check.
        self.db = CanDatabase(dbname, logLevel = logLevel)
        creator = Creator(self.db)
        #creator.createSchema()
        #creator.createIndices()
        self.db.beginTransaction()

    def __del__(self):
        self.close()

    def close(self):
        self.db.close()

    def getCursor(self):
        return self.db.getCursor()

    def insertOrReplaceStatement(self, insert, cur, tname, columns, *values):
        """
        """
        verb = "INSERT" if insert else "REPLACE"
        try:
            placeholder = ','.join("?" * len(values))
            stmt = "{} INTO {}({}) VALUES({})".format(verb, tname, columns, placeholder)
            cur.execute(stmt, [*values])
        except sqlite3.DatabaseError as e:
            msg = "{} - Data: {}".format(str(e), values)
            self.logger.error(msg)
            raise
        else:
            pass

    def insertStatement(self, cur, tname, columns, *values):
        """
        """
        return self.insertOrReplaceStatement(True, cur, tname, columns, *values)

    def replaceStatement(self, cur, tname, columns, *values):
        """
        """
        return self.insertOrReplaceStatement(False, cur, tname, columns, *values)

    def writeDbcFile(self, filename = None):
        """
        """
        pass

    def readDbcFile(self, filename = None):
        """
        """
        pass

    def renderDbcFile(self):
        """
        """
        pass

    def addNode(self, name, comment):
        """
        """
        cur = self.getCursor()
        self.db.insertStatement(cur, "Node", "Name, Comment", name, comment)

    def addMessage(self, identifier, name, size):
        """
        """
        pass

    def addAttributeDefinition(self):
        """
        """
        pass

    def addEnvironmentVariable(self, name, vartype, valueRange, unit, initialValue = None, accessNodes = None):
        """
        """
        pass

    def addCategory(self):
        """
        """
        pass

    def addValuetable(self):
        """
        """
        pass

    def _searchTableForName(self, tableName, glob = None, regex = None):
        """
        """
        if glob is None and regex is None:
            where = None
        elif glob is not None:
            where = "Name GLOB '{}'".format(glob)
        elif regex is not None:
            where = "Name REGEXP '{}'".format(regex)
        return self.db.fetchFromTable(tableName, where = where)

    def nodes(self, glob = None, regex = None):
        """
        """
        for item in self._searchTableForName("Node", glob, regex):
            yield Node(self, item['RID'], item['Name'], item['Comment'])

    def node(self, name):
        """
        """

    def messages(self, glob = None, regex = None):
        """
        """
        for item in self._searchTableForName("Message", glob, regex):
            yield Message(self, item['RID'], item['Name'], CANAddress(item['Message_ID']), item['DLC'], item['Sender'], item['Comment'])

    def applicableAttributes(self, objectType):
        """
        """
        if not objectType in AttributeType.__members__.values():
            self.logger.error("applicableAttributes(): invalid objecttype '{}'.".format(objectType))
            return None
        yield from self.db.fetchFromTable("Attribute_Definition", where = "objecttype = {}".format(objectType))

    def attributeValue(self, oid, attrDef):
        return self.db.fetchSingleRow("Attribute_Value", column = "*", where = "Object_ID = {} AND Attribute_Definition = {}".format(oid, attrDef))

