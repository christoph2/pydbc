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

class Creator(object):

    def __init__(self, db):
        self.db = db
        self.logger = Logger(__name__)

    def dropTables(self):
        cur = self.db.getCursor()
        self.db.beginTransaction()
        for item in TABLES:
            self.logger.debug("Dropping table '{}'.".format(item))
            try:
                cur.execute("DROP TABLE IF EXISTS {}".format(item))
            except sqlite3.DatabaseError as e:
                self.logger.error("Deletion of table '{}' failed : '{}'".format(item, str(e)))
                raise
        for item in VIEWS:
            self.logger.debug("Dropping view '{}'.".format(item))
            try:
                cur.execute("DROP VIEW IF EXISTS {}".format(item))
            except sqlite3.DatabaseError as e:
                self.logger.error("Deletion of view '{}' failed : '{}'".format(item, str(e)))
                raise
        self.db.commitTransaction()

    def createSchema(self):
        cur = self.db.getCursor()
        self.db.beginTransaction()

        #cur.execute("PRAGMA foreign_keys = ON")
        #cur.execute('PRAGMA synchronous = OFF')
        #cur.execute('PRAGMA LOCKING_MODE = EXCLUSIVE')
        #self.cur.execute('PRAGMA journal_mode = MEMORY')
        #self.cur.execute('PRAGMA journal_mode = WAL')

        for item in SCHEMA:
            self.logger.info("Executing SQL statement: {}".format(item))
            #print("Executing SQL statement: {}".format(item))
            res = cur.execute(item)
        self.insertDefaults(cur)
        self.db.commitTransaction()

    def insertDefaults(self, cur):
        for item in DEFAULTS:
            res = cur.execute(item)

    def createIndices(self):
        cur = self.db.getCursor()
        self.db.beginTransaction()
        for item in INDICES:
            #print(item)
            res = cur.execute(item)
        self.db.commitTransaction()

