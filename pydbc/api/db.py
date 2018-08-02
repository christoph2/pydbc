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

from pydbc.types import AttributeType, CANAddress, EnvVarType, EnvVarAccessType
from pydbc.db.creator import Creator
from pydbc.db import CanDatabase
from pydbc.api.base import BaseObject
from pydbc.api.message import Message
from pydbc.api.node import Node
from pydbc.api.envvar import EnvVar
from pydbc.api.limits import Limits
from pydbc.api.valuetable import ValueTable, Value
from pydbc.logger import Logger


DBC_EXTENSION = "dbc"
DB_EXTENSION = "vndb"


class DuplicateRecordError(Exception): pass


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

    def addEnvVar(self, name, vartype, valueRange, unit, initialValue = None, accessNodes = None):
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
        cur = self.db.getCursor()
        return self.db.fetchFromTable(cur, tableName, where = where)

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

    def messageSignal(self, messageId, signalId):
        cur = self.db.getCursor()
        where = "Message = {} AND Signal = {}".format(messageId, signalId)
        return self.db.fetchSingleRow(cur, tname = "Message_Signal", column = "*", where = where)

    def envVar(self, name):
        """
        """

    def envVars(self, glob = None, regex = None):
        """
        """
        for item in self._searchTableForName("EnvVar", glob, regex):
            yield EnvVar(self, item['RID'], item['Name'], EnvVarType(item['Type']), item['Unit'], EnvVarAccessType(item['Access'] & 0x0f), item['Size'],
                item['Startup_Value'], Limits(item['Minimum'], item['Maximum']), item['Comment']
            )

    def applicableAttributes(self, objectType):
        """
        """
        if not objectType in AttributeType.__members__.values():
            self.logger.error("applicableAttributes(): invalid objecttype '{}'.".format(objectType))
            return None
        cur = self.db.getCursor()
        yield from self.db.fetchFromTable(cur, "Attribute_Definition", where = "objecttype = {}".format(objectType))


    def singleAttribute(self, objectType, name):
        """
        """
        if not objectType in AttributeType.__members__.values():
            self.logger.error("applicableAttributes(): invalid objecttype '{}'.".format(objectType))
            return None
        cur = self.db.getCursor()
        return self.db.fetchSingleRow(cur, "Attribute_Definition", column = "*", where = "objecttype = {} AND Name = '{}'".format(objectType, name))

    def attributeValue(self, oid, attrDef):
        cur = self.db.getCursor()
        return self.db.fetchSingleRow(cur, "Attribute_Value", column = "*", where = "Object_ID = {} AND Attribute_Definition = {}".format(oid, attrDef))

    def createValueTableObjects(self, objectType, rid):
        vt = None
        cur = self.db.getCursor()
        cur.execute("""SELECT Object_RID, Valuetable AS VT_RID, Name, Comment FROM Object_Valuetable AS t1,
        Valuetable AS t2 WHERE t1.Valuetable = t2.RID AND Object_Type = ? AND Object_RID = ?""", [objectType, rid])
        row = cur.fetchone()
        if row:
            res = self.db.createDictFromRow(row, cur.description)
            cur.execute("SELECT Value, Value_Description FROM Value_Description WHERE Valuetable = ?", [res['VT_RID']])
            rows = cur.fetchall()
            values = []
            for value, desc in rows:
                val = Value(desc, int(value))
                values.append(val)
            if values:
                vt = ValueTable(objectType, res['Object_RID'], res['VT_RID'], res['Name'], res['Comment'], values)
                #print("VT:", vt)
                return vt


