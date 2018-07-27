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


from pydbc.types import AttributeType, MultiplexingType, ByteOrderType, ValueType
from pydbc.api.base import BaseObject
from pydbc.api.signal import Formula, Multiplexing, Signal
from pydbc.api.limits import Limits


class Message(BaseObject):
    """
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

    def signals(self):
        for signal in self.database.db.signals(self.key):
            ms = self.database.messageSignal(self.rid, signal['RID'])
            mpxValue = ms['Multiplexor_Value']
            mpxDependent = ms['Multiplex_Dependent']
            mpxSignal = ms['Multiplexor_Signal']
            if mpxSignal == 1:
                mpxType = MultiplexingType.MULTIPLEXOR
            elif mpxDependent == 1:
                mpxType = MultiplexingType.DEPENDENT
            else:
                mpxType = MultiplexingType.NONE
            mpx = Multiplexing(mpxType, mpxValue)
            yield Signal(self.database, self.rid, signal['RID'], signal['Name'], ms['Offset'], signal['Bitsize'], ByteOrderType(signal['Byteorder']),
                         ValueType(signal['Valuetype']), Formula(signal['Formula_Factor'], signal['Formula_Offset']),
                         Limits(signal['Minimum'], signal['Maximum']), signal['Unit'], mpx if mpx.type != MultiplexingType.NONE else None,
                         signal['Comment']
                    )

