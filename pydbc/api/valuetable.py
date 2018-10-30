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

from pydbc.types import ValueTableType


class Value:

    def __init__(self, name, value):
        self.name = name
        self.value = value

    def __str__(self):
        return "'{}' -> {}".format(self.name, self.value)

    __repr__ = __str__


class ValueTable:
    """
    """

    def __init__(self, database, objectType, objectRid):
        self.database = database
        self.objectType = objectType
        self.objectRid = objectRid
        cur = self.database.getCursor()
        cur.execute("""SELECT Object_RID, Valuetable AS VT_RID, Name, Comment FROM Object_Valuetable AS t1,
        Valuetable AS t2 WHERE t1.Valuetable = t2.RID AND Object_Type = ? AND Object_RID = ?""", [objectType, objectRid])
        row = cur.fetchone()
        values = []
        if row:
            res = self.database.db.createDictFromRow(row, cur.description)
            self.name = res['Name']
            self.comment = res['Comment']
            cur.execute("SELECT Value, Value_Description FROM Value_Description WHERE Valuetable = ?", [res['VT_RID']])
            rows = cur.fetchall()
            for value, desc in rows:
                val = Value(desc, int(value))
                values.append(val)
        else:
            self.name = ''
            self.comment = ''
        self.values = [] if values is None else values

    def addValue(self, name, value):
        self.values.append(Value(name, value))

    def __str__(self):
        return '{}(name = "{}", comment = "{}", values = {})'.format(self.__class__.__name__, self.name, self.comment or "", self.values)

    __repr__ = __str__

