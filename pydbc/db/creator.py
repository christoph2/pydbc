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


from pydbc.db.schema import TABLES, VIEWS, SCHEMA, INDICES, TRIGGER

from pydbc.logger import Logger

class Creator(object):

    def __init__(self, db):
        self.db = db
        self.logger = Logger('db.creator')

    def run(self):
        self.dropTables()
        self.createSchema()

    def dropTables(self):
        cur = self.db.getCursor()
        self.db.beginTransaction()
        for item in TABLES:
            #print(item)
            res = cur.execute("DROP TABLE IF EXISTS {}".format(item))
        for item in VIEWS:
            #print(item)
            res = cur.execute("DROP VIEW IF EXISTS {}".format(item))
        self.db.commitTransaction()

    def createSchema(self):
        cur = self.db.getCursor()
        cur.execute("PRAGMA foreign_keys = ON")
        cur.execute('PRAGMA synchronous = OFF')
        cur.execute('PRAGMA LOCKING_MODE = EXCLUSIVE')
        #self.cur.execute('PRAGMA journal_mode = MEMORY')
        #self.cur.execute('PRAGMA journal_mode = WAL')
        self.db.beginTransaction()
        for item in SCHEMA:
            #print(item)
            res = cur.execute(item)
        self.db.commitTransaction()

    def createIndices(self):
        cur = self.db.getCursor()
        self.db.beginTransaction()
        for item in INDICES:
            #print(item)
            res = cur.execute(item)
        self.db.commitTransaction()
