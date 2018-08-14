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

import sqlite3

from pydbc.db.schema import TABLES, VIEWS, SCHEMA, INDICES, TRIGGER, DEFAULTS
from pydbc.logger import Logger
from pydbc.version import VNDB_SCHEMA_VERSION


class Creator(object):

    def __init__(self, db):
        self.db = db
        self.logger = Logger(__name__)

    def drop(self, entity, items):
        cur = self.db.getCursor()
        for item in items:
            self.logger.debug("Dropping {} '{}'.".format(entity.lower(), item))
            try:
                cur.execute("DROP {} IF EXISTS {}".format(entity.upper(), item))
            except sqlite3.DatabaseError as e:
                self.logger.error("Deletion of {} '{}' failed : '{}'".format(entity.lower(), item, str(e)))
                raise

    def dropTables(self):
        cur = self.db.getCursor()
        self.db.beginTransaction()
        self.drop("table", TABLES)
        self.drop("view", VIEWS)
        self.db.commitTransaction()

    def createSchema(self):
        cur = self.db.getCursor()
        self.executeItems(SCHEMA, "table")
        self.executeItems(TRIGGER, "trigger")
        self.insertDefaults(cur)

    def insertDefaults(self, cur):
        self.executeItems(DEFAULTS, "default")

    def createIndices(self):
        self.executeItems(INDICES, "index")

    def createMetaData(self):
        sql = "INSERT OR REPLACE INTO VndbMeta(RID, Schema_Version) VALUES(1, {})".format(VNDB_SCHEMA_VERSION)
        self.executeItem(sql, "meta-data", transactional = True)

    def executeItem(self, item, name, cur = None, transactional = False):
        if not cur:
            cur = self.db.getCursor()
        if transactional:
            self.db.beginTransaction()
        self.logger.debug("Creating {} '{}'.".format(name, item))
        try:
            res = cur.execute(item)
        except sqlite3.DatabaseError as e:
            self.logger.error("Creation of {} '{}' failed : '{}'".format(name, item, str(e)))
            #raise
        if transactional:
            self.db.commitTransaction()

    def executeItems(self, items, name):
        cur = self.db.getCursor()
        self.db.beginTransaction()
        for item in items:
            self.executeItem(item, name, cur)
        self.db.commitTransaction()

