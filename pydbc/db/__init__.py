#!/usr/bin/env python
# -*- coding: utf-8 -*-

__copyright__ = """
   pySART - Simplified AUTOSAR-Toolkit for Python.

   (C) 2010-2025 by Christoph Schueler <cpu12.gems.googlemail.com>

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
__author__ = "Christoph Schueler"
__version__ = "0.1.0"

import mmap
import re
import sqlite3
from functools import partial

from sqlalchemy import (
    types,
    orm,
    event,
    create_engine,
    text,
)
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker

from pydbc.db import model
from pydbc.logger import Logger

DB_EXTENSION = "vndb"

CACHE_SIZE = 4  # MB
PAGE_SIZE = mmap.PAGESIZE


def calculateCacheSize(value):
    return -(value // PAGE_SIZE)


REGEXER_CACHE = {}


def regexer(value, expr):
    if not REGEXER_CACHE.get(expr):
        REGEXER_CACHE[expr] = re.compile(expr, re.UNICODE)
    re_expr = REGEXER_CACHE[expr]
    return re_expr.match(value) is not None


INITIAL_DATA = {
    "node": (
        {
            "rid": 0,
            "node_id": 0,
            "name": "Vector__XXX",
            "comment": "Dummy node for non-existent senders/receivers.",
            "type_": "Node",
        },
    ),
}
"""
    INSERT INTO message(comment,rid,name,message_id,dlc,sender,type) VALUES(
        'This is a message for not used signals, created by Vector CANdb++ DBC OLE DB Provider.',
        1,
        'VECTOR__INDEPENDENT_SIG_MSG',
        3221225472,
        0,
        0,
        'Message');
"""


def _inserter(data, target, conn, **kws):
    for row in data:
        k, v = row.keys(), row.values()
        keys = ", ".join([x for x in k])
        values = ", ".join([repr(x) for x in v])
        stmt = text("INSERT INTO {}({}) VALUES ({})".format(target.name, keys, values))
        conn.execute(stmt)


def loadInitialData(target):
    data = INITIAL_DATA[target.__table__.fullname]
    event.listen(target.__table__, "after_create", partial(_inserter, data))


class MyCustomEnum(types.TypeDecorator):
    impl = types.Integer

    def __init__(self, enum_values, *l, **kw):
        types.TypeDecorator.__init__(self, *l, **kw)
        self._enum_values = enum_values

    def convert_bind_param(self, value, engine):
        result = self.impl.convert_bind_param(value, engine)
        if result not in self._enum_values:
            raise TypeError("Value %s must be one of %s" % (result, self._enum_values))
        return result

    def convert_result_value(self, value, engine):
        "Do nothing here"
        return self.impl.convert_result_value(value, engine)


@event.listens_for(Engine, "connect")
def set_sqlite3_pragmas(dbapi_connection, connection_record):
    dbapi_connection.create_function("REGEXP", 2, regexer)
    cursor = dbapi_connection.cursor()
    # cursor.execute("PRAGMA jornal_mode=WAL")
    cursor.execute("PRAGMA FOREIGN_KEYS=ON")
    cursor.execute("PRAGMA PAGE_SIZE={}".format(PAGE_SIZE))
    cursor.execute(
        "PRAGMA CACHE_SIZE={}".format(calculateCacheSize(CACHE_SIZE * 1024 * 1024))
    )
    cursor.execute("PRAGMA SYNCHRONOUS=OFF")  # FULL
    cursor.execute("PRAGMA LOCKING_MODE=EXCLUSIVE")  # NORMAL
    cursor.execute("PRAGMA TEMP_STORE=MEMORY")  # FILE
    cursor.close()


class VNDB(object):
    """ """

    def __init__(self, filename: str = ":memory:", debug: bool = False, logLevel: str = "INFO", create: bool = True,
                 autocommit: bool = False):
        if filename == ":memory:":
            self.dbname = ""
        else:
            if not filename.lower().endswith(DB_EXTENSION):
                self.dbname = "{}.{}".format(filename, DB_EXTENSION)
            else:
                self.dbname = filename
        self._engine = create_engine(
            "sqlite:///{}".format(self.dbname),
            echo=debug,
            connect_args={
                "detect_types": sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES,
                "isolation_level": "IMMEDIATE",
            },
            native_datetime=True,
            # autocommit=autocommit
        )
        SessionFactory = sessionmaker(self._engine, autoflush=False)    # autocommit=autocommit
        self._session = SessionFactory()
        self._metadata = model.Base.metadata
        if create == True:
            model.Base.metadata.create_all(self.engine)
            self.session.flush()
            self.session.commit()
        self.logger = Logger(__name__, level=logLevel)

    @classmethod
    def _open_or_create(
            cls, filename=":memory:", debug=False, logLevel="INFO", create=True, autocommit=False,
    ):
        """ """
        inst = cls(filename, debug, logLevel, create, autocommit)
        return inst

    @classmethod
    def create(cls, filename=":memory:", debug=False, logLevel="INFO", autocommit: bool=False):
        """ """
        return cls._open_or_create(filename, debug, logLevel, True, autocommit)

    @classmethod
    def open(cls, filename=":memory:", debug=False, logLevel="INFO", autocommit: bool=False):
        """ """
        return cls._open_or_create(filename, debug, logLevel, False, autocommit)

    def close(self):
        """ """
        self.session.close()
        self.engine.dispose()

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
        """ """

    def commit_transaction(self):
        """ """

    def rollback_transaction(self):
        """ """


loadInitialData(model.Node)
