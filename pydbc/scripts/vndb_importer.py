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

import os
import pathlib

from pydbc.parser import ParserWrapper
from pydbc.dbcListener import DbcListener
from pydbc.ldfListener import LdfListener
from pydbc.ncfListener import NcfListener
from pydbc.types import FileType


def parseFile(pth, filetype, debug = False, remove_file = False, logLevel = "WARN"):
    if filetype == FileType.DBC:
        grammar = 'dbc'
        start_symbol = 'dbcfile'
        listenerClass = DbcListener
    elif filetype == FileType.LDF:
        grammar = 'ldf'
        start_symbol = 'lin_description_file'
        listenerClass = LdfListener
    elif filetype == FileType.NCF:
        grammar = 'ncf'
        start_symbol = 'toplevel'
        listenerClass = NcfListener
    else:
        raise ValueError("Invalid filetype '{}'".format(filetype))
    parser = ParserWrapper(grammar, start_symbol, listenerClass, debug = debug, logLevel = logLevel)
    print("Processing '{}'".format(pth))

    dbfn = "{}.vndb".format(pth.stem)
    if remove_file:
        try:
            os.unlink(dbfn)
        except Exception:
            pass
    session = parser.parseFromFile(str(pth))
    print("OK, done.\n", flush = True)
    return session

def get_file_type(pth):
    suffix = pth.suffix.lower()
    if suffix == '.dbc':
        result = FileType.DBC
    elif suffix == '.ldf':
        result = FileType.LDF
    elif suffix == '.ncf':
        result = FileType.NCF
    else:
        result = None
    return result

def importFile(pth, logLevel):
    file_type = get_file_type(pth)
    session = parseFile(pth, file_type, remove_file = True, logLevel = logLevel)


def main():
    footer = "CAVEAT: In this version vndb_importer is DESTRUCTIVE, i.e. no merging happens!"
    parser = argparse.ArgumentParser(description = 'Import .dbc file into Vehicle Network Database.', epilog = footer)
    parser.add_argument("vehicle_file", help = ".dbc or .ldf file(s) to import", nargs = "+")
    parser.add_argument("-k", dest = 'keepDirectory', action = "store_true", default = False,
        help = "keep directory; otherwise create db in current directory"
    )
    parser.add_argument("-l", help = "loglevel [warn | info | error | debug]", dest = "loglevel", type = str, default = "warn")
    parser.add_argument("-w", help = "Format output for Windows console.", dest = "winout", action = "store_true")
    parser.add_argument("-u", help = "Generate UTF-8 encoded output (otherwise Latin-1).", dest = "ucout", action = "store_true")
    args = parser.parse_args()
    ucout = args.ucout
    for arg in args.vehicle_file:
        for pth in pathlib.Path().glob(arg):
            importFile(pth, args.loglevel)

if __name__ == '__main__':
    main()
