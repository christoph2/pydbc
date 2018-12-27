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

import io
import os
from pprint import pprint
import pkgutil
import sqlite3
import sys

import antlr4
import colorama

from pydbc import parser
from pydbc.dbcListener import DbcListener
from pydbc.db import CanDatabase
from pydbc.db.creator import Creator
from pydbc.db.loader import Loader
from pydbc.template import renderTemplateFromText

from pydbc.db.common import Queries


template = pkgutil.get_data("pydbc", "cgen/templates/dbc.tmpl")

def coloredText(color, msg):
    return "{}{}".format(color, msg)

def errorText(msg):
    return coloredText(colorama.Fore.RED, msg)

def successText(msg):
    return coloredText(colorama.Fore.GREEN, msg)

def progressText(msg):
    return coloredText(colorama.Fore.BLUE, msg)

def resetColorStyle():
    print(colorama.Style.RESET_ALL, end = "", flush = True)

def execute(fun, name, *args):
    try:
        fun(*args)
    except Exception as e:
        msg = errorText("   Exiting import function due to exception while {}".format(name))
        if not isinstance(e, sqlite3.DatabaseError):
            msg += ": {}".format(str(e))
        print("{}\n".format(msg), flush = True)
        print(str(e))
        resetColorStyle()
        #sys.exit(1)
        return False
    else:
        return True

def importFile(name):
    global ucout

    pth, fname = os.path.split(name)
    fnbase, fnext = os.path.splitext(fname)
    db = CanDatabase(r"{}.vndb".format(fnbase))

    print(progressText("Processing file '{}'...").format(name), flush = True)
    resetColorStyle()

    cr = Creator(db)
    if not execute(cr.dropTables, "dropping tables"):
        return
    if not execute(cr.createSchema, "creating schema"):
        return

    pa = parser.ParserWrapper('dbc', 'dbcfile', DbcListener)

    try:
        tree = pa.parseFromFile("{}".format(name), encoding = "utf-8" if ucout else "latin-1", trace = False)
    except Exception as e:
        print(errorText("   Exiting import function due to exception while parsing: {}\n".format(str(e))), flush = True)
        resetColorStyle()
        return

    #print("Finished ANTLR parsing.", flush = True)

    loader = Loader(db, Queries)

    if not execute(loader.insertValues, "inserting values", tree):
        return
    if not execute(cr.createIndices, "creating indices"):
        return
    if not execute(cr.createMetaData, "creating meta-data"):
        return

    #pprint(tree, indent = 4)

    namespace = dict(db = Queries(db))
    #print("Rending template...", flush = True)

#    db.outputDbc(0, "{}.render".format(fnbase))
    res = renderTemplateFromText(template, namespace, formatExceptions = True, encoding = "utf-8" if ucout else "latin-1")
    with io.open("{}.render".format(fnbase), "w", encoding = "utf-8" if ucout else "latin-1", newline = "\r\n") as outf:
        outf.write(res)

    print(successText("OK, done.\n"), flush = True)
    resetColorStyle()
    #print("-" * 80, flush = True)

ucout = False

def main():
    global ucout

    footer = "CAVEAT: In this version vndb_importer is DESTRUCTIVE, i.e. no merging happens!"
    parser = argparse.ArgumentParser(description = 'Import .dbc file into Vehicle Network Database.', epilog = footer)
    parser.add_argument("dbcfile", help = ".dbc file(s) to import", nargs = "+")
    parser.add_argument("-k", dest = 'keepDirectory', action = "store_true", default = False,
        help = "keep directory; otherwise create db in current directory"
    )
    parser.add_argument("-l", help = "loglevel [warn | info | error | debug]", dest = "loglevel", type = str, default = "warn")
    parser.add_argument("-w", help = "Format output for Windows console.", dest = "winout", action = "store_true")
    parser.add_argument("-u", help = "Generate UTF-8 encoded output (otherwise Latin-1).", dest = "ucout", action = "store_true")
    args = parser.parse_args()
    colorama.init(convert = args.winout, strip = False)
    ucout = args.ucout
    for name in args.dbcfile:
        importFile(name)

if __name__ == '__main__':
    main()

