#!/usr/bin/env python
# -*- coding: utf-8 -*-

__copyright__ = """
   pySART - Simplified AUTOSAR-Toolkit for Python.

   (C) 2010-2019 by Christoph Schueler <cpu12.gems.googlemail.com>

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

from datetime import datetime
from functools import partial
import mmap
import os
import sqlite3
import sys

from sqlalchemy import (MetaData, schema, types, orm, event,
    create_engine, Column, ForeignKey, ForeignKeyConstraint, func,
    PassiveDefault, UniqueConstraint, inspect
)

from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.engine import Engine
from sqlalchemy.sql import exists
#from sqlalchemy.ext.automap import automap_base

from pydbc.logger import Logger
from pydbc.db import model

DB_EXTENSION    = "vndb"

CACHE_SIZE      = 4 # MB
PAGE_SIZE       = mmap.PAGESIZE

def calculateCacheSize(value):
    return -(value // PAGE_SIZE)

def regexer(expr, value):
    return re.match(expr, value, re.UNICODE) is not None

class MyCustomEnum(types.TypeDecorator):

    impl=types.Integer

    def __init__(self, enum_values, *l, **kw):
        types.TypeDecorator.__init__(self, *l, **kw)
        self._enum_values = enum_values

    def convert_bind_param(self, value, engine):
        result = self.impl.convert_bind_param(value, engine)
        if result not in self._enum_values:
            raise TypeError("Value %s must be one of %s" % (result, self._enum_values))
        return result

    def convert_result_value(self, value, engine):
        'Do nothing here'
        return self.impl.convert_result_value(value, engine)

@event.listens_for(Engine, "connect")
def set_sqlite3_pragmas(dbapi_connection, connection_record):
    dbapi_connection.create_function("REGEXP", 2, regexer)
    cursor = dbapi_connection.cursor()
    #cursor.execute("PRAGMA jornal_mode=WAL")
    cursor.execute("PRAGMA FOREIGN_KEYS=ON")
    cursor.execute("PRAGMA PAGE_SIZE={}".format(PAGE_SIZE))
    cursor.execute("PRAGMA CACHE_SIZE={}".format(calculateCacheSize(CACHE_SIZE * 1024 * 1024)))
    cursor.execute("PRAGMA SYNCHRONOUS=OFF") # FULL
    cursor.execute("PRAGMA LOCKING_MODE=EXCLUSIVE") # NORMAL
    cursor.execute("PRAGMA TEMP_STORE=MEMORY")  # FILE
    cursor.close()


class CanDatabase(object):

    def __init__(self, filename, debug = False, logLevel = 'INFO'):
        if filename == ':memory:':
            self.dbname = ""
        else:
            if not filename.lower().endswith(DB_EXTENSION):
               self.dbname = "{}.{}".format(filename, DB_EXTENSION)
            else:
               self.dbname = filename
            #try:
            #    os.unlink(self.dbname)
            #except:
            #    pass
        self._engine = create_engine("sqlite:///{}".format(self.dbname), echo = debug,
            connect_args={'detect_types': sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES},
        native_datetime = True)

        self._session = orm.Session(self._engine, autoflush = True, autocommit = False)
        self._metadata = model.Base.metadata
        model.Base.metadata.create_all(self.engine)
        model.loadInitialData(model.Node)
        self.session.flush()
        self.session.commit()
        self.logger = Logger(__name__, level = logLevel)
        """

        from sqlalchemy import distinct, func
        stmt = select([func.count(distinct(users_table.c.name))])
        # ODER
        stmt = select([func.count(users_table.c.name.distinct())])

        ##
        ##
        from sqlalchemy import bindparam

        stmt = select([users_table]) where(users_table.c.name == bindparam('username'))
        result = connection.execute(stmt, username='wendy')
        """

    @property
    def engine(self):
        return self._engine

    @property
    def metadata(self):
        return self._metadata

    @property
    def session(self):
        return self._session

    def begin_transaction(self):
        """
        """

    def commit_transaction(self):
        """
        """

    def rollback_transaction(self):
        """
        """
