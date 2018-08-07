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


class Limits:

    def __init__(self, min = 0, max = 0):
        self.typeCheck(min)
        self.typeCheck(max)
        if not (min is None and max is None) and max < min:
            raise ValueError("max is smaller than min.")
        self._min = min
        self._max = max

    def _getMin(self):
        return self._min

    def _setMin(self, value):
        self.typeCheck(value)
        if (value is not None and self.max is not None) and self.max < value:
            raise ValueError("min is larger than max.")
        self._min = value

    def _getMax(self):
        return self._max

    def _setMax(self, value):
        self.typeCheck(value)
        if (self.min is not None and value is not None) and value < self.min:
            raise ValueError("max is smaller than min.")
        self._max = value

    def typeCheck(self, value):
        if not (isinstance(value, (int, float)) or value is None):
            raise TypeError("Value needs to be int, float, or None.")

    def __eq__(self, other):
        return self.min == other.min and self.max == other.max

    min = property(_getMin, _setMin)
    max = property(_getMax, _setMax)

    def __str__(self):
        minimum = "N/A" if self.min is None else self.min
        maximum = "N/A" if self.max is None else self.max
        return "{}(min = {}, max = {})".format(self.__class__.__name__, minimum, maximum)

    __repr__ = __str__

