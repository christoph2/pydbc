#!/usr/bin/env python
# -*- coding: utf-8 -*-

__copyright__ = """
   pySART - Simplified AUTOSAR-Toolkit for Python.

   (C) 2010-2020 by Christoph Schueler <cpu12.gems.googlemail.com>

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

CAN_EXTENDED_IDENTIFIER = 0x80000000

class VndbType(enum.IntEnum):
    SINGLE_NETWORK = 0
    MULTIPLE_NETWORKS = 1


class BusType(enum.IntEnum):
    CAN = 0
    LIN = 1


class FileType(enum.IntEnum):
    DBC = 0
    LDF = 1
    NCF = 2

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
    """

    """

    def __init__(self, priority, reserved, datapage, pdu_format, pdu_specific, source_address):
        self.priority = priority
        self.reserved = reserved
        self.datapage = datapage
        self.pdu_format = pdu_format
        self.pdu_specific = pdu_specific
        self.source_address = source_address

    @classmethod
    def from_int(klass, canID):
        # TODO: check for extID
        canID &= (~CAN_EXTENDED_IDENTIFIER)
        priority = (canID & 0x1c000000) >> 26
        reserved = (canID & 0x2000000) >> 25
        datapage = (canID & 0x1000000) >> 24
        pdu_format = (canID & 0xff0000) >> 16
        pdu_specific = (canID & 0xff00) >> 8
        source_address = canID & 0xff
        return klass(priority, reserved, datapage, pdu_format, pdu_specific, source_address)

    @property
    def pgn(self):
        return (self.pdu_format << 8) | self.pdu_specific

    @pgn.setter
    def pgn(self, value):
        """

        """
        self.pdu_format = (value & 0xff00) >> 8
        self.pdu_specific = (value & 0xff)


    @property
    def canID(self):
        """
        """
        return ((self.priority & 0x07) << 26) | ((self.reserved & 0x01) << 25) | ((self.datapage & 0x01) << 24) | \
            ((self.pdu_format & 0xff) << 16) |  ((self.pdu_specific & 0xff) << 8) | (self.source_address & 0xff)


    @canID.setter
    def canID(self, value):
        pass

    def __str__(self):
        return "{}(priority = {}, reserved = {}, datapage = {}, pdu_format = {}, pdu_specific = {}, source_address = {})".\
            format(self.__class__.__name__, self.priority, self.reserved, self.datapage, self.pdu_format,
            self.pdu_specific, self.source_address
        )

    __repr__ = __str__


class LinProductIdType(object):
    """

    """

    def __init__(self, supplier_id, function_id, variant):
        self.supplier_id = supplier_id & 0xffff
        self.function_id = function_id & 0xffff
        self.variant = variant & 0xff

    def __str__(self):
        return "LinProductIdType(supplier_id = {}, function_id = {}, variant = {})".format(
            self.supplier_id, self.function_id, self.variant)

    __repr__ = __str__
