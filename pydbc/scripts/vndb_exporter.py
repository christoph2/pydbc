#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
"""

__copyright__ = """
   pySART - Simplified AUTOSAR-Toolkit for Python.

    ( C) 2010-2020 by Christoph Schueler <cpu12.gems.googlemail.com>

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

import argparse
import io
import pathlib
import sys

from pydbc.db.imex import DbcExporter, LdfExporter
import pydbc.db.model as model

def exportFile(pth):
    fnext = pth.suffix[ 1 : ].lower()

    print("Processing '{}'".format(pth))
    #exporter = DbcExporter(pth)
    exporter = LdfExporter(pth, debug = False)

    exporter.run()
    print("OK, done.\n", flush = True)

exportFile(pathlib.Path(sys.argv[1]))


