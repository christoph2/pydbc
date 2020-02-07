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

import io
import os
import pkgutil

import sqlalchemy as sa

from pydbc.logger import Logger
from pydbc.db import VNDB
from pydbc.db.creator import Creator
from pydbc import parser
from pydbc.dbcListener import DbcListener
from pydbc.ldfListener import LdfListener
from pydbc.ncfListener import NcfListener
from pydbc.template import renderTemplateFromText
import pydbc.db.model as model



"""
def execute(fun, name, *args):
    try:
        fun(*args)
    except Exception as e:
        msg = "   Exiting import function due to exception while {}".format(name)
        if not isinstance(e, sqlite3.DatabaseError):
            msg += ": {}".format(str(e))
        print("{}\n".format(msg), flush = True)
        print(str(e))
        #sys.exit(1)
        return False
    else:
        return True
"""

class Importer:
    """
    """
    def __init__(self, name, encoding = "latin-1", debug = False):
        self.logger = Logger(__name__)
        self.encoding = encoding
        self.fname = name.parts[-1]
        self.fnbase = name.stem
        self.fnext = name.suffix[ 1 : ].lower()
        self.fabsolute = name.absolute()

        dbname = "{}.vndb".format(self.fname)
        print("unlinking", dbname)
        try:
            os.unlink(dbname)
        except Exception:
            pass


        self.db = VNDB(r"{}.vndb".format(self.fnbase), debug = debug)
        self.creator = Creator(self.db)
        #self.run()

    def create_part1(self):
        pass
        #if not execute(self.creator.dropTables, "dropping tables"):
        #    return
        #if not execute(self.creator.createSchema, "creating schema"):
        #    return

    def create_part2(self):
        if not execute(self.creator.createIndices, "creating indices"):
            return
        if not execute(self.creator.createMetaData, "creating meta-data"):
            return

    def parse(self):
        try:
            self.tree = self.parser.parseFromFile("{}".format(self.fabsolute), encoding = self.encoding, trace = False)
        except Exception as e:
            self.logger.error("Exiting import function due to exception while parsing: {}\n".format(str(e)))
            return

    def parseString(self, dbcString):
        try:
            self.tree = self.parser.parseFromString(dbcString, encoding = self.encoding, trace = False)
        except Exception as e:
            self.logger.error("Exiting import function due to exception while parsing: {}\n".format(str(e)))
            return

    def loadDB(self):
        self.loader.insertValues(self.tree)
        #if not execute(self.loader.insertValues, "inserting values", self.tree):
        #    return

    def run(self):
        self.create_part1()
        self.parse()
        self.loadDB()
        #self.create_part2()

class DbcImporter(Importer):
    """
    """

    def __init__(self, name):
        super(DbcImporter, self).__init__(name)
        self.parser = parser.ParserWrapper('dbc', 'dbcfile', DbcListener)
        self.loader = DbcLoader(self.db)

class LdfImporter(Importer):
    """
    """

    def __init__(self, name):
        super(LdfImporter, self).__init__(name)
        self.parser = parser.ParserWrapper('ldf', 'lin_description_file', LdfListener)
        self.loader = LdfLoader(self.db)

class NcfImporter(Importer):
    """
    """

    def __init__(self, name):
        super(NcfImporter, self).__init__(name)
        self.parser = parser.ParserWrapper('ncf', 'toplevel', NcfListener)
        self.loader = NcfLoader(self.db)

def createImporter(ext: str):
    """

    """
    if ext == "dbc":
        return DbcImporter
    elif ext == "ldf":
        return LdfImporter
    elif ext == "ncf":
        return NcfImporter
    else:
        raise ValueError("Invalid file-extension '{}'".format(ext))

def fetch_attributes(db):
    # Attribute structure is currently to inconvenient for ad-hoc queries, so pre-fetch them.

    from collections import defaultdict
    from itertools import groupby
    from operator import itemgetter

    from pydbc.types import AttributeType, ValueType, CategoryType

    data = db.session.query(model.Attribute_Value.num_value, model.Attribute_Value.string_value,
        model.Attribute_Definition.valuetype, model.Attribute_Definition.array, model.Attribute_Definition.objecttype,
        model.Attribute_Value.object_id, model.Attribute_Definition.name).join(model.Attribute_Definition).\
        order_by(model.Attribute_Definition.objecttype)
    result = {}
    groups = []
    keyfunc = itemgetter(4)
    data = sorted(data, key = keyfunc)
    for k, g in groupby(data, keyfunc):
        group = list(g)
        result[AttributeType(k).name] = defaultdict(dict)
        groups.append(list(group))
        keyfunc = itemgetter(5)
        group2 = sorted(group, key = keyfunc)
        for k2, g2 in groupby(group2, keyfunc):
            for num_value, string_value, value_type, array, object_type, object_id, name in list(g2):
                if num_value is None and string_value is None:
                    value = None
                else:
                    if array:
                        conv = float if value_type == ValueType.FLOAT else int
                        value = [conv(x) for x in string_value.split(";")]
                    else:
                        if value_type in (ValueType.INT, ValueType.FLOAT):
                            conv = float if value_type == ValueType.FLOAT else int
                            value = conv(num_value)
                        else:
                            value = string_value
                item = { "value": value }
                result[AttributeType(k).name][k2][name] = value
    return result

class Exporter:
    """
    """
    def __init__(self, name, encoding = "latin-1"):
        self.logger = Logger(__name__)
        self.encoding = encoding
        self.fname = name.parts[-1]
        self.fnbase = name.stem
        self.fnext = name.suffix[ 1 : ].lower()
        self.fabsolute = name.absolute()

        self.db = VNDB(r"{}.vndb".format(self.fnbase))
        #res = renderTemplateFromText(self.TEMPLATE, namespace, formatExceptions = True, encoding = "utf-8" if ucout else "latin-1")

    def run(self):

        #xxx = self.db.session.query(model.Attribute_Value).join(model.Attribute_Definition).\
        #    filter(model.Attribute_Definition.name == "LIN_is_master").one()
        #node = self.db.session.query(model.Node).filter(model.Node.rid == xxx.object_id).one()
        #print("ATTRS:", fetch_attributes(self.db))
        namespace = dict(db = self.db, model = model, attributes = fetch_attributes(self.db), sa = sa)
        res = renderTemplateFromText(self.TEMPLATE, namespace, formatExceptions = False, encoding = self.encoding)
        #print("RES:", res)
        with io.open("{}.render".format(self.fnbase), "w", encoding = self.encoding, newline = "\r\n") as outf:
            outf.write(res)

class DbcExporter(Exporter):
    """
    """
    TEMPLATE = pkgutil.get_data("pydbc", "cgen/templates/dbc.tmpl")

class LdfExporter(Exporter):
    """
    """
    TEMPLATE = pkgutil.get_data("pydbc", "cgen/templates/ldf.tmpl")