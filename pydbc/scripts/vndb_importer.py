#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
"""

__copyright__ = """
   pySART - Simplified AUTOSAR-Toolkit for Python.

    ( C) 2010-2019 by Christoph Schueler <cpu12.gems.googlemail.com>

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

from pydbc.db.imex import createImporter

def importFile(pth):
    fnext = pth.suffix[ 1 : ].lower()

    importer = createImporter(fnext)
    imp = importer(pth)
    imp.run()

    print("OK, done.\n", flush = True)


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
            importFile(pth)

if __name__ == '__main__':
    main()

