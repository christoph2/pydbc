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

from pydbc.types import AttributeType, MultiplexingType
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
        ('comment', 'Comment'),
    )

    def __init__(self, database, rid, name, identifier, dlc, comment):
        super(Message, self).__init__(database)
        self._rid = rid
        self._name = name
        self._identifier = identifier
        self._dlc = dlc
        self._comment = comment

    def signalsByRid(self, messageId):
        cur = self.getCursor()
        res = cur.execute("""SELECT * FROM message_signal AS t1, signal AS t2 WHERE t1.message = ? AND t1.signal = t2.RID""", [messageId])
        while True:
            row = cur.fetchone()
            if row is None:
                return
            else:
                yield self.db.createDictFromRow(row, cur.description)

    def signalByRidAndName(self, rid, name):
        cur = self.getCursor()
        cur.execute("""SELECT * FROM signal WHERE rid IN (SELECT t1.signal FROM message_signal AS t1, signal AS t2
        WHERE t1.message = 2 AND t1.signal = t2.RID)""", [rid])
        result = cur.fetchone()
        return self.db.createDictFromRow(result, cur.description)

    def signals(self):
        for signal in self.database.queries.signals(self.key):
            yield Signal(self.database, self.rid, signal)

    def signal(self, name):
        """
        """
        cur = self.getCursor()
        cur.execute("""SELECT * FROM signal WHERE rid = (SELECT t1.signal FROM message_signal AS t1, signal AS t2
        WHERE t1.message = ? AND t2.name = ? AND t1.signal = t2.RID)""", [self.rid, name])
        result = cur.fetchone()
        if result:
            return self.db.createDictFromRow(result, cur.description)
        else:
            return None

    """
        def messages(self, glob = None, regex = None):
        for item in self._searchTableForName("Message", glob, regex):
            yield Message(self, item['RID'], item['Name'], CANAddress(item['Message_ID']), item['DLC'], item['Comment'])

    def message(self, name):
        cur = self.db.getCursor()
        where = "Name = '{}'".format(name)
        item = self.db.fetchSingleRow(cur, tname = "Message", column = "*", where = where)
        if item:
            return Message(self, item['RID'], item['Name'], item['Message_ID'], item['DLC'], item['Comment'])
        else:
            return None
    """

    def addSignal(self, name, startBit, bitSize, byteOrder, valueType, unit, formula, limits,
                  multiplexing = MultiplexingType.NONE, values = None, comment = None):
        """
        """
    # TODO: __iter__ for signals.

    @property
    def rid(self):
        return self._rid

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def identifier(self):
        return self._identifier

    @identifier.setter
    def identifier(self, value):
        self._identifier = value

    @property
    def dlc(self):
        return self._dlc

    @dlc.setter
    def dlc(self, value):
        self._dlc = value

    @property
    def comment(self):
        return self._comment

    @comment.setter
    def comment(self, value):
        self._comment = value
