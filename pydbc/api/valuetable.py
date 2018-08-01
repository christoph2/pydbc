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

    def __init__(self, objectType, objectRid, vtRid, name, comment):
        self.objectType = objectType
        self.objectRid = objectRid
        self.vtRid = vtRid
        self.name = name
        self.comment = comment
        self.values = []

    def addValue(self, value):
        if not isinstance(value, Value):
            raise TypeError("value must be of type Value.")
        self.values.append(value)

    def __str__(self):
        return '{}(name = "{}", comment = "{}" values = {})'.format(self.__class__.__name__, self.name, self.comment or "", self.values)

    __repr__ = __str__

