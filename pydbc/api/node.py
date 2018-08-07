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

from pydbc.types import AttributeType
from pydbc.api.base import BaseObject


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
        self._rid = rid
        self._name = name
        self._comment = comment

    @property
    def rid(self):
        return self._rid

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        if not isinstance(value, str):
            raise TypeError("Value must be of type string.")
        self._name = value

    @property
    def comment(self):
        return self._comment

    @comment.setter
    def comment(self, value):
        if not isinstance(value, str):
            raise TypeError("Value must be of type string.")
        self._comment = value

