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

class AttributeType(enum.IntEnum):
    NODE = 0
    MESSAGE = 1
    SIGNAL = 2
    ENV_VAR = 3
    GENERAL = 4


class ValueType(enum.IntEnum):
    INT = 0
    HEX = 1
    FLOAT = 2
    STRING = 3
    ENUM = 4


class IdentifierType(enum.IntEnum):
    STANDARD = 0
    EXTENDED = 1

EXTENDED_ID_MASK = 0x80000000


class AddressBaseType:

    def __init__(self):
        pass


class CANAddress(AddressBaseType):
    """
    """

    def __init__(self, rawId):
        if (rawId & EXTENDED_ID_MASK) == EXTENDED_ID_MASK:
            self.mtype = IdentifierType.EXTENDED
            self.mid = rawId & (~0x80000000)
        else:
            self.mtype = IdentifierType.STANDARD
            self.mid = mid = rawId

    def __str__(self):
        """
        """
        return "{}({:08x} [{}])".format(self.__class__.__name__, self.mid, self.mtype.name)

    def __int__(self):
        """
        """
        value = self.mid
        if self.mtype == IdentifierType.EXTENDED:
            value |= EXTENDED_ID_MASK
        return value


    __repr__ = __str__


class J1939Address(AddressBaseType):

    def __init__(self, rawId):
        # TODO: check for extID
        rawId &= (~0x80000000)
        self.priority = (rawId & 0x1c000000) >> 26
        self.reserved = (rawId & 0x2000000) >> 25
        self.datapage = (rawId & 0x1000000) >> 24
        self.pduFormat = (rawId & 0xff0000) >> 16
        self.pduSpecific = (rawId & 0xff00) >> 8
        self.sourceAddress = rawId & 0xff

    def __str__(self):
        return "{}(prio = {} r = {} dp = {} pf = {:02x} ps = {:02x} sa = {:02x} )".format(self.__class__.__name__,
            self.priority, self.reserved, self.datapage, self.pduFormat, self.pduSpecific, self.sourceAddress
        )

    __repr__ = __str__
