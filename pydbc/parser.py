#!/usr/bin/env python
# -*- coding: utf-8 -*-

__copyright__ = """
   pySART - Simplified AUTOSAR-Toolkit for Python.

   (C) 2010-2020 by Christoph Schueler <cpu12.gems.googlemail.com>

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

import codecs
import importlib
import os
from pprint import pprint
import sys

import six
import antlr4
import antlr4.tree

from sqlalchemy.sql.expression import literal, bindparam
from sqlalchemy.ext import baked

from pydbc.logger import Logger
from pydbc.db import VNDB
from pydbc.db.model import (
    Dbc_Version, Message, Message_Signal, Network, Node, Signal, Value_Description,
    Valuetable, EnvironmentVariablesData, EnvVar, Attribute_Definition, Attribute_Value,
    Node_TxMessage, Node_RxSignal, Category_Definition, Category_Value, AttributeRel_Value,
    Signal_Group_Signal, Signal_Group, Vndb_Protocol, Object_Valuetable
)

def indent(level):
    print(" " * level,)

def dump(tree, level = 0):
    indent(level)
    if isinstance(tree, antlr4.TerminalNode):
        print(tree.symbol.text)
    else:
        print("({}".format(tree.value))
        level += 1
        for child in tree.children:
            dump(child, level)
        level -= 1
    indent(level)
    print(")")


def toInt(number, base = 10):
    """

    """
    try:
        res = int(number, base)
    except ValueError as e:
        res = None
    return res

def toFloat(number):
    """

    """
    try:
        res = float(number)
    except ValueError as e:
        res = None
    return res

class BaseListener(antlr4.ParseTreeListener):
    """
    """

    value = []

    def __init__(self, database, logLevel = 'INFO'):
        self.db = database
        self.logger = Logger(__name__, level = logLevel)
        super(BaseListener, self).__init__()
        self.session = database.session
        self.bakery = baked.bakery()
        self.bake_common_queries()

    def bake_common_queries(self):
        self.ATTRIBUTE_DEFINITION_BY_NAME = self.bakery(lambda session: self.session.query(Attribute_Definition).\
            filter(Attribute_Definition.name == bindparam('name')))
        self.MESSAGE_BY_NAME = self.bakery(lambda session: session.query(Message).filter(Message.name == bindparam('name')))
        self.NODE_BY_NAME = self.bakery(lambda session: session.query(Node).filter(Node.name == bindparam('name')))
        self.NODE_BY_RID = self.bakery(lambda session: session.query(Node).filter(Node.rid == bindparam('rid')))
        self.SIGNAL_BY_NAME = self.bakery(lambda session: session.query(Signal).filter(Signal.name == bindparam('name')))
        self.SIGNAL_BY_RID = self.bakery(lambda session: session.query(Signal).filter(Signal.rid == bindparam('rid')))

    def log_insertion(self, table_name):
        self.logger.debug("Inserting values for '{}'.".format(table_name))

    def getList(self, attr):
        return [x for x in attr] if attr else []

    def getTerminal(self, attr, default = None):
        return attr.text if attr else default

    def getValue(self, attr, default = None):
        return attr.value if attr else default

    def exitIntValue(self, ctx):
        if ctx.i:
            ctx.value = toInt(ctx.i.text, 10)
        elif ctx.h:
            ctx.value = toInt(ctx.h.text, 16)
        else:
            ctx.value = None

    def exitFloatValue(self, ctx):
        ctx.value = toFloat(ctx.f.text) if ctx.f else None

    def exitNumber(self, ctx):
        if ctx.i:
            value = ctx.i.value
        elif ctx.f:
            value = ctx.f.value
        else:
            value = None
        ctx.value = value

    def exitStringValue(self, ctx):
        value = ctx.s.text.strip('"') if ctx.s else None
        ctx.value = value

    def exitIdentifierValue(self, ctx):
        value = ctx.i.text if ctx.i else None
        value = None if value == "<missing C_IDENTIFIER>" else value
        ctx.value = value

    def _formatMessage(self, msg, location):
        return "[{0}:{1}] {2}".format(location.start.line, location.start.column + 1, msg)

    def _log(self, method, msg, location = None):
        if location:
            method(self._formatMessage(msg, location))
        else:
            method(msg)

    def info(self, msg, location = None):
        self._log(self.info.warn, msg, location)

    def warn(self, msg, location = None):
        self._log(self.logger.warn, msg, location)

    def error(self, msg, location = None):
        self._log(self.logger.warn, msg, location)

    def debug(self, msg, location = None):
        self._log(self.logger.warn, msg, location)


class ParserWrapper(object):
    """
    """
    def __init__(self, grammarName, startSymbol, listenerClass, debug = False, logLevel = 'INFO'):
        self.grammarName = grammarName
        self.startSymbol = startSymbol
        self.lexerModule, self.lexerClass = self._load('Lexer')
        self.parserModule, self.parserClass = self._load('Parser')
        self.listenerClass = listenerClass
        self.debug = debug
        self.logLevel = logLevel

    def __del__(self):
        pass

    def _load(self, name):
        className = '{0}{1}'.format(self.grammarName, name)
        moduleName = 'pydbc.py{0}.{1}'.format(2 if six.PY2 else 3, className)
        module = importlib.import_module(moduleName)
        klass = getattr(module, className)
        return (module, klass, )

    def parse(self, input, trace = False):
        self.db = VNDB(self.fnbase, debug = self.debug)
        lexer = self.lexerClass(input)
        tokenStream = antlr4.CommonTokenStream(lexer)
        parser = self.parserClass(tokenStream)
        parser.setTrace(trace)
        meth = getattr(parser, self.startSymbol)
        self._syntaxErrors = parser._syntaxErrors
        tree = meth()
        if self.listenerClass:
            listener = self.listenerClass(self.db, self.logLevel)
            walker = antlr4.ParseTreeWalker()
            walker.walk(listener, tree)
        self.db.session.commit()
        return self.db.session

    def parseFromFile(self, filename, encoding = 'latin-1', trace = False):
        pth, fname = os.path.split(filename)
        self.fnbase = os.path.splitext(fname)[0]
        return self.parse(ParserWrapper.stringStream(filename, encoding), trace)

    def parseFromString(self, buf, encoding = 'latin-1', trace = False, dbname = ":memory:"):
        self.fnbase = dbname
        return self.parse(antlr4.InputStream(buf), trace)

    @staticmethod
    def stringStream(fname, encoding = 'latin-1'):
        return antlr4.InputStream(codecs.open(fname, encoding = encoding).read())

    def _getNumberOfSyntaxErrors(self):
        return self._syntaxErrors

    numberOfSyntaxErrors = property(_getNumberOfSyntaxErrors)


