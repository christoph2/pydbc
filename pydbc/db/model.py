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

import datetime
from functools import partial
import mmap
import re

from sqlalchemy import (MetaData, schema, types, orm, event,
    create_engine, Column, ForeignKey, ForeignKeyConstraint, func,
    PassiveDefault, UniqueConstraint, CheckConstraint
)
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.ext.associationproxy import association_proxy
#from sqlalchemy.engine import Engine
from sqlalchemy.orm import relationship

Base = declarative_base()

INITIAL_DATA = {
    'node': (
                {"rid": 0, "node_id": 0, "name": 'Vector__XXX', "comment": 'Dummy node for non-existent senders/receivers.'},
            ),
}

def _inserter(data, target, conn, **kws):
    for row in data:
        k, v = row.keys(), row.values()
        keys = ', '.join([x for x in k])
        values = ', '.join([repr(x) for x in v])
        stmt = "INSERT INTO {}({}) VALUES ({})".format(target.name, keys, values)
        conn.execute(stmt)

def loadInitialData(target):
    data = INITIAL_DATA[target.__table__.fullname]
    event.listen(target.__table__, 'after_create', partial(_inserter, data))

class MixInBase(object):

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    def __repr__(self):
        columns = [c.name for c in self.__class__.__table__.c]
        result = []
        for name, value in [(n, getattr(self, n)) for n in columns]:
            if isinstance(value, str):
                result.append("{} = '{}'".format(name, value))
            else:
                result.append("{} = {}".format(name, value))
        return "{}({})".format(self.__class__.__name__, ", ".join(result))

class CommentableMixIn(object):
    comment = Column(types.Unicode(255), default = None)

class MinMaxMixIn(object):
    minimum = Column(types.Float, default = 0.0)
    maximum = Column(types.Float, default = 0.0)

class RidMixIn(MixInBase):
    rid = Column("rid", types.Integer, primary_key = True)

def StdInteger(default = 0, primary_key = False, unique = False):
    return Column(types.Integer, default = default, nullable = False,    # PassiveDefault(str(default))
        primary_key = primary_key, unique = unique)

class Node(Base, RidMixIn, CommentableMixIn):

    name = Column(types.Unicode(255), nullable = False, unique = True, index= True)
    node_id = StdInteger()

class Message_Signal(Base, MixInBase):

    message_id = Column(types.Integer,
        ForeignKey("message.rid", onupdate = "CASCADE", ondelete = "RESTRICT"),
        nullable = False, default = 0, primary_key = True
    )
    signal_id = Column(types.Integer,
        ForeignKey("signal.rid", onupdate = "CASCADE", ondelete = "RESTRICT"),
        nullable = False, default = 0, primary_key = True
    )
    offset = Column(types.Integer, nullable = False, default = 0)
    multiplexor_signal = Column(types.Integer, default = 0)
    multiplex_dependent = Column(types.Boolean)
    multiplexor_value    = Column(types.Integer)
    message = relationship("Message", backref = "signals")
    signal = relationship("Signal", backref = "messages")
    
class Message(Base, RidMixIn, CommentableMixIn):

    name = Column(types.Unicode(255), nullable = False, unique = True, index = True)
    message_id = StdInteger(unique = True)
    dlc = StdInteger()
    sender = StdInteger()

class Signal(Base, RidMixIn, CommentableMixIn):

    name = Column(types.Unicode(255), nullable = False, index = True)
    bitsize = StdInteger()
    byteorder = StdInteger(default = 1)
    sign = StdInteger(default = 1)
    valuetype = StdInteger()
    formula_factor = Column(types.Float, default = 1.0)
    formula_offset = Column(types.Float, default = 0.0)
    minimum = Column(types.Float, default = 0.0)
    maximum = Column(types.Float, default = 0.0)
    unit = Column(types.Unicode(255))

class Network(Base, RidMixIn, CommentableMixIn):

    name = Column(types.Unicode(255), nullable = False, unique = True, index = True)
    protocol = StdInteger()
    baudrate = StdInteger()

class Attribute_Definition(Base, RidMixIn, CommentableMixIn):

    name = Column(types.Unicode(255), nullable = False, unique = True, index = True)
    objecttype = StdInteger()
    valuetype = StdInteger()
    minimum = Column(types.Float, default = 0.0)
    maximum = Column(types.Float, default = 0.0)
    enumvalues = Column(types.TEXT)
    default_number = Column(types.Float, default = 0.0)
    default_string = Column(types.Unicode(255))

class Attribute_Value(Base, MixInBase):

    object_id = Column(types.Integer, nullable = False, default = 0, primary_key = True)
    attribute_definition = Column(types.Integer,
        ForeignKey("attribute_definition.rid", onupdate = "CASCADE", ondelete = "RESTRICT"),
        nullable = False, default = 0, primary_key = True,
    )
    num_value = Column(types.Float, default = 0.0)
    string_value = Column(types.TEXT)

class linAttribute_Definition(Base, RidMixIn, CommentableMixIn):

    name = Column(types.Unicode(255), nullable = False, unique = True, index = True)
    objecttype = StdInteger()
    valuetype = StdInteger()
    minimum = Column(types.Float, default = 0.0)
    maximum = Column(types.Float, default = 0.0)
    enumvalues = Column(types.TEXT)
    default_number = Column(types.Float, default = 0.0)
    default_string = Column(types.Unicode(255))

class linAttribute_Value(Base, MixInBase):

    object_id = Column(types.Integer, nullable = False, default = 0, primary_key = True)
    attribute_definition = Column(types.Integer,
        ForeignKey("linattribute_definition.rid", onupdate = "CASCADE", ondelete = "RESTRICT"),
        nullable = False, default = 0, primary_key = True,
    )
    num_value = Column(types.Float, default = 0.0)
    string_value = Column(types.TEXT)

class AttributeRel_Value(Base, MixInBase):

    object_id = Column(types.Integer, nullable = False, default = 0, primary_key = True)
    attribute_definition = Column(types.Integer,
        ForeignKey("attribute_definition.rid", onupdate = "CASCADE", ondelete = "RESTRICT"),
        nullable = False, default = 0, primary_key = True,
    )
    num_value = Column(types.Float, default = 0.0)
    string_value = Column(types.TEXT)
    opt_object_id_1 = Column(types.Integer, nullable = False, default = 0, primary_key = True)
    opt_object_id_2 = Column(types.Integer, nullable = False, default = 0, primary_key = True)
    blob_value = Column(types.BLOB)


class Vndb_Meta(Base, RidMixIn):

    schema_version = StdInteger()
    vndb_type = StdInteger()
    created = Column(types.DateTime, default = datetime.datetime.now) 

class Vndb_Migrations(Base, RidMixIn):

    app = Column(types.Unicode(255), nullable = False)
    name = Column(types.Unicode(255), nullable = False)
    applied = Column(types.DateTime,  func.now)


class Vndb_Protocol(Base, MixInBase):

    network = Column(types.Integer,
        ForeignKey("network.rid", onupdate = "CASCADE", ondelete = "RESTRICT"),
        nullable = False, default = 0, primary_key = True,
    )
    name = Column(types.Unicode(255), nullable = False)
    specific = Column(types.Unicode(255), nullable = False)

class ECU(Base, RidMixIn, CommentableMixIn):

    name = Column(types.Unicode(255), nullable = False, unique = True, index = True)

class EnvVar(Base, RidMixIn, CommentableMixIn):

    name = Column(types.Unicode(255), nullable = False, unique = True, index = True)
    type = StdInteger()
    unit = Column(types.Unicode(255), default = None)
    minimum = Column(types.Float, default = 0.0)
    maximum = Column(types.Float, default = 0.0)
    startup_value = Column(types.Float, default = 0.0)
    size = StdInteger()
    access = StdInteger()
    
    accessingNodes = relationship("Node", secondary = "envvar_accessnode")

class ECU_EnvVar(Base, MixInBase):

    ecu = Column(types.Integer,
        ForeignKey("ecu.rid", onupdate = "CASCADE", ondelete = "RESTRICT"),
        nullable = False, default = 0, primary_key = True,
    )
    env_var = Column(types.Integer,
        ForeignKey("envvar.rid", onupdate = "CASCADE", ondelete = "RESTRICT"),
        nullable = False, default = 0, primary_key = True,
    )

class ECU_Node(Base, MixInBase):
    ecu = Column(types.Integer,
        ForeignKey("ecu.rid", onupdate = "CASCADE", ondelete = "RESTRICT"),
        nullable = False, default = 0, primary_key = True,
    )
    node = Column(types.Integer,
        ForeignKey("node.rid", onupdate = "CASCADE", ondelete = "RESTRICT"),
        nullable = False, default = 0, primary_key = True,
    )

class Gateway_Signal(Base, RidMixIn, CommentableMixIn):

    vehicle_id = Column(types.Integer, nullable = False, default = 0)
    dest_signal = Column(types.Integer, nullable = False, default = 0)
    dest_network = Column(types.Integer, nullable = False, default = 0)
    dest_message = Column(types.Integer, nullable = False, default = 0)
    dest_transmitter = Column(types.Integer, nullable = False, default = 0)
    gateway = Column(types.Integer, nullable = False, default = 0)
    source_signal = Column(types.Integer, nullable = False, default = 0)
    source_network = Column(types.Integer, nullable = False, default = 0)
    source_message = Column(types.Integer, nullable = False, default = 0)
    source_receiver = Column(types.Integer, nullable = False, default = 0)
    reserved_id1 = Column(types.Integer, nullable = False, default = 0)

class Node_Group(Base, RidMixIn, CommentableMixIn):

    name = Column(types.Unicode(255), nullable = False, unique = True, index = True)
    node_object_type = Column(types.Integer, nullable = False, default = 0)
    node_group_type = Column(types.Integer, nullable = False, default = 0)

class Node_Group_Object(Base, MixInBase):
    parent_type = Column(types.Integer, nullable = False, default = 0, primary_key = True)
    parent_rid = Column(types.Integer, nullable = False, default = 0, primary_key = True)
    object_type = Column(types.Integer, nullable = False, default = 0, primary_key = True)
    object_rid = Column(types.Integer, nullable = False, default = 0, primary_key = True)
    object_rid2 = Column(types.Integer, nullable = False, default = 0, primary_key = True)
    opt_object_ref_1 = Column(types.Integer, nullable = False, default = 0)
    opt_object_ref_2 = Column(types.Integer, nullable = False, default = 0)
    opt_object_value = Column(types.Integer, nullable = False, default = 0)

class Network_Node(Base, MixInBase):

    network = Column(types.Integer,
        ForeignKey("network.rid", onupdate = "CASCADE", ondelete = "RESTRICT"),
        nullable = False, default = 0, primary_key = True
    )
    node = Column(types.Integer,
        ForeignKey("node.rid", onupdate = "CASCADE", ondelete = "RESTRICT"),
        nullable = False, default = 0, primary_key = True
    )

class Node_RxSig(Base, MixInBase):

    node = Column(types.Integer,
        ForeignKey("node.rid", onupdate = "CASCADE", ondelete = "RESTRICT"),
        nullable = False, default = 0, primary_key = True
    )
    signal = Column(types.Integer,
        ForeignKey("signal.rid", onupdate = "CASCADE", ondelete = "RESTRICT"),
        nullable = False, default = 0, primary_key = True
    )

class Node_RxSignal(Base, MixInBase):

    node = Column(types.Integer,
        ForeignKey("node.rid", onupdate = "CASCADE", ondelete = "RESTRICT"),
        nullable = False, default = 0, primary_key = True
    )
    message = Column(types.Integer,
        ForeignKey("message.rid", onupdate = "CASCADE", ondelete = "RESTRICT"),
        nullable = False, default = 0, primary_key = True
    )
    signal = Column(types.Integer,
        ForeignKey("signal.rid", onupdate = "CASCADE", ondelete = "RESTRICT"),
        nullable = False, default = 0, primary_key = True
    )

class Node_TxMessage(Base, MixInBase):

    node = Column(types.Integer,
        ForeignKey("node.rid", onupdate = "CASCADE", ondelete = "RESTRICT"),
        nullable = False, default = 0, primary_key = True
    )
    message = Column(types.Integer,
        ForeignKey("message.rid", onupdate = "CASCADE", ondelete = "RESTRICT"),
        nullable = False, default = 0, primary_key = True
    )

class Node_TxSig(Base, MixInBase):

    node = Column(types.Integer,
        ForeignKey("node.rid", onupdate = "CASCADE", ondelete = "RESTRICT"),
        nullable = False, default = 0, primary_key = True
    )
    signal = Column(types.Integer,
        ForeignKey("signal.rid", onupdate = "CASCADE", ondelete = "RESTRICT"),
        nullable = False, default = 0, primary_key = True
    )

class Signal_Group(Base, RidMixIn):

    name = Column(types.Unicode(255), nullable = False)
    value = Column(types.Integer, nullable = False, default = 0)
    message = Column(types.Integer,
        ForeignKey("message.rid", onupdate = "CASCADE", ondelete = "RESTRICT"),
        nullable = False, default = 0, unique = True
    )
    UniqueConstraint("Message", "Name")

class Signal_Group_Signal(Base, MixInBase):

    signal_group = Column(types.Integer,
        ForeignKey("signal_group.rid", onupdate = "CASCADE", ondelete = "RESTRICT"),
        nullable = False, default = 0, primary_key = True
    )
    message = Column(types.Integer,
        ForeignKey("message.rid", onupdate = "CASCADE", ondelete = "RESTRICT"),
        nullable = False, default = 0, primary_key = True
    )
    signal = Column(types.Integer,
        ForeignKey("signal.rid", onupdate = "CASCADE", ondelete = "RESTRICT"),
        nullable = False, default = 0, primary_key = True
    )

class Valuetable(Base, RidMixIn, CommentableMixIn):

    name = Column(types.Unicode(255), nullable = False, index = True)

class Object_Valuetable(Base, MixInBase):

    object_type = Column(types.Integer, nullable = False, default = 0, primary_key = True)
    object_rid = Column(types.Integer, nullable = False, default = 0, primary_key = True)
    valuetable = Column(types.Integer,
        ForeignKey("valuetable.rid", onupdate = "CASCADE", ondelete = "RESTRICT"),
        nullable = False, default = 0
    )

class Value_Description(Base, MixInBase):

    valuetable = Column(types.Integer,
        ForeignKey("valuetable.rid", onupdate = "CASCADE", ondelete = "RESTRICT"),
        nullable = False, default = 0, primary_key = True
    )
    value = Column(types.Float, nullable = False, default = 0.0, primary_key = True)
    value_description = Column(types.Unicode(255), nullable = False)


class Vehicle(Base, RidMixIn, CommentableMixIn):

    name = Column(types.Unicode(255), nullable = False, unique = True, index = True)

class Vehicle_ECU(Base, MixInBase):

    vehicle = Column(types.Integer,
        ForeignKey("vehicle.rid", onupdate = "CASCADE", ondelete = "RESTRICT"),
        nullable = False, default = 0, primary_key = True
    )

    ecu = Column(types.Integer,
        ForeignKey("ecu.rid", onupdate = "CASCADE", ondelete = "RESTRICT"),
        nullable = False, default = 0, primary_key = True
    )

class Vehicle_Network(Base, MixInBase):

    vehicle = Column(types.Integer,
        ForeignKey("vehicle.rid", onupdate = "CASCADE", ondelete = "RESTRICT"),
        nullable = False, default = 0, primary_key = True
    )

    network = Column(types.Integer,
        ForeignKey("network.rid", onupdate = "CASCADE", ondelete = "RESTRICT"),
        nullable = False, default = 0, primary_key = True
    )

class Versioninfo(Base, MixInBase):

    obj_type = Column(types.Integer, nullable = False, default = 0, primary_key = True)
    obj_rid = Column(types.Integer, nullable = False, default = 0, primary_key = True)
    version_number = Column(types.Integer, nullable = False, default = 0)
    is_modified = Column(types.Boolean, nullable = False, default = False)

class Category_Definition(Base, RidMixIn):

    name = Column(types.Unicode(255), nullable = False)
    key = Column(types.Integer, nullable = False, default = 0, unique = True)
    level = Column(types.Integer, nullable = False, default = 0)

class Category_Value(Base, MixInBase):

    object_id = Column(types.Integer, nullable = False, default = 0, primary_key = True)
    category_definition = Column(types.Integer,
        ForeignKey("category_definition.key", onupdate = "CASCADE", ondelete = "RESTRICT"),
        nullable = False, default = 0
    )
    objecttype = Column(types.Integer, nullable = False, default = 0, primary_key = True)

class Dbc_Version(Base, RidMixIn):

    version_string = Column(types.Unicode(255), nullable = False, default = '')
    network = Column(types.Integer, nullable = False, default = 0, unique = True)

class EnvVar_AccessNode(Base, MixInBase):

    envvar_id = Column(types.Integer,
        ForeignKey("envvar.rid", onupdate = "CASCADE", ondelete = "RESTRICT"),
        nullable = False, default = 0, primary_key = True
    )
    node_id = Column(types.Integer,
        ForeignKey("node.rid", onupdate = "CASCADE", ondelete = "RESTRICT"),
        nullable = False, default = 0, primary_key = True
    )
    #envvar = relationship("EnvVar", backref = "nodes")
    #node = relationship("Node", backref = "envvars")

class EnvironmentVariablesData(Base, MixInBase):

    name = Column(types.Unicode(255), nullable = False, primary_key = True)
    value = Column(types.Integer, nullable = False)
