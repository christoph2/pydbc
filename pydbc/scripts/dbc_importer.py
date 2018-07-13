#!/usr/bin/env python
# -*- coding: utf-8 -*-

__copyright__ = """
   pySART - Simplified AUTOSAR-Toolkit for Python.

    ( C) 2010-2018 by Christoph Schueler <cpu12.gems.googlemail.com>

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

import importlib

import antlr4

import io
import os
from pprint import pprint
import pkgutil
import sqlite3
import sys
from pydbc import dbc

from pydbc.db import CanDatabase
from pydbc.db.creator import Creator
from pydbc.db.loader import Loader
from pydbc.template import renderTemplateFromText

##
## Complementary tool: vndb_exporter
##

template = pkgutil.get_data("pydbc", "cgen/templates/dbc.tmpl")

def execute(fun, name, *args):
    try:
        fun(*args)
    except Exception as e:
        msg = "  Terminating dbc-importer due to exception while {}".format(name)
        if not isinstance(e, sqlite3.DatabaseError):
            msg += ": {}".format(str(e))
        print("\n", msg)            
        sys.exit(1)

def main():
    footer = "CAVEAT: In this version dbc_importer is DESTRUCTIVE, i.e. no merging happens!"
    parser = argparse.ArgumentParser(description = 'Import .dbc file into Vehicle Network Database.', epilog = footer)
    
    #parser.add_argument('dbcfile', metavar='infile', type=str, nargs='1',
    #                    help='.dbc file to import.')
    
    parser.add_argument("dbcfile", help = ".dbc file to import")
    
    #parser.add_argument('--sum', dest='accumulate', action='store_const',
    #                    const=sum, default=max,
    #                    help='sum the integers (default: find the max)')

    # "-k" help = "keep directory -- otherwise create db in current directory"
    # "-l" loglevel default = "warn"
    # "-d" debuglevel
    

    args = parser.parse_args()
    print(args)
    #print(args.accumulate(args.integers))
    pth, fname = os.path.split(args.dbcfile)
    fnbase, fnext = os.path.splitext(fname)
    db = CanDatabase(r"{}.vndb".format(fnbase))
    
    cr = Creator(db)
    execute(cr.dropTables, "dropping tables")
    execute(cr.createSchema, "creating schema")
    
    print("DBName: ", db.filename)

    pa = dbc.ParserWrapper('dbc', 'dbcfile')

#    print("NAMES:", sys.argv[1], args.dbcfile, fname)
    tree = pa.parseFromFile(args.dbcfile, trace = False)

    print("Finished ANTLR parsing.")

    loader = Loader(db)
        
    execute(loader.insertValues, "inserting values", tree)
    execute(cr.createIndices, "creating indices")
    
    #pprint(tree, indent = 4)

    namespace = dict(db = db)
    print("Rending template...")
    res = renderTemplateFromText(template, namespace)
    #print(res)
    with io.open("{}.render".format(fnbase), "w", encoding = "latin-1", newline = "\n") as outf:
        outf.write(res)
    print("Finished.")
    print("-" * 80)

if __name__ == '__main__':
    main()

