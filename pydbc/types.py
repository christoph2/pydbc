#!/usr/bin/env python
# -*- coding: utf-8 -*-

__copyright__ = """
   pySART - Simplified AUTOSAR-Toolkit for Python.

   (C) 2010-2019 by Christoph Schueler <cpu12.gems.googlemail.com>

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


class VndbType(enum.IntEnum):
    SINGLE_NETWORK = 0
    MULTIPLE_NETWORKS = 1


class AttributeType(enum.IntEnum):
    NODE        = 0
    MESSAGE     = 1
    SIGNAL      = 2
    ENV_VAR     = 3
    NETWORK     = 4
    REL_NODE    = 5
    REL_SIGNAL  = 6
    REL_ENV_VAR = 7


class ValueType(enum.IntEnum):
    INT = 0
    HEX = 1
    FLOAT = 2
    STRING = 3
    ENUM = 4


class ByteOrderType(enum.IntEnum):
    MOTOROLA = 0
    INTEL = 1


class SignalType(enum.IntEnum):
    SINT = 0
    FLOAT32 = 1
    FLOAT64 = 2
    UINT = 8


class MultiplexingType(enum.IntEnum):
    NONE = 0
    MULTIPLEXOR = 1
    DEPENDENT = 2


class IdentifierType(enum.IntEnum):
    STANDARD = 0
    EXTENDED = 1


class EnvVarType(enum.IntEnum):
    INT = 0
    FLOAT = 1
    STRING = 2
    DATA = 3


class EnvVarAccessType(enum.IntEnum):
    UNRESTRICTED = 0
    READ = 1
    WRITE = 2
    READ_WRITE = 3


class ValueTableType(enum.IntEnum):
    SIGNAL  = 0
    ENV_VAR = 1


class CategoryType(enum.IntEnum):
    NODE = 0
    MESSAGE = 1
    ENV_VAR = 2


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
            self.value = rawId & (~0x80000000)
        else:
            self.mtype = IdentifierType.STANDARD
            self.value = mid = rawId

    def __str__(self):
        """
        """
        return "{}({:08x} [{}])".format(self.__class__.__name__, self.value, self.mtype.name)

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
