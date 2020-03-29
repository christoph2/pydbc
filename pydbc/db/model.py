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

import datetime
from functools import partial
import mmap
import re

from sqlalchemy import (MetaData, schema, types, orm, event,
    create_engine, Column, ForeignKey, ForeignKeyConstraint, func,
    PassiveDefault, UniqueConstraint, CheckConstraint, select
)
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.ext.mutable import Mutable
from sqlalchemy.ext.orderinglist import ordering_list
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import relationship, with_polymorphic, validates

from pydbc.types import (J1939Address, LinProductIdType, ByteOrderType, ValueType)

Base = declarative_base()

INIT_VALUE = re.compile("(?P<array>\d+(?:,\d+)+) | (?P<scalar>\d+)", re.VERBOSE)

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

def StdInteger(default = 0, primary_key = False, unique = False, nullable = False):
    return Column(types.Integer, default = default, nullable = nullable,    # PassiveDefault(str(default))
        primary_key = primary_key, unique = unique)

def StdFloat(default = 0.0, primary_key = False, unique = False, nullable = False):
    return Column(types.Integer, default = default, nullable = nullable,
        primary_key = primary_key, unique = unique)

"""
    order_items = relationship(
        "OrderItem", cascade="all, delete-orphan", backref="order"
    )
"""


class Node(Base, RidMixIn, CommentableMixIn):

    name = Column(types.Unicode(255), nullable = False, unique = True, index= True)
    node_id = StdInteger()
    type = Column(types.String(256))
    __mapper_args__ = {
        "polymorphic_identity": "Node",
        "polymorphic_on": type,
    }

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
    multiplexor_value = Column(types.Integer)

    signal = relationship("Signal", lazy = "joined")

    def __init__(self, signal, message, offset, multiplexor_signal = None,
            multiplex_dependent = None, multiplexor_value = None):
        self.signal = signal
        self.message = message
        self.offset = offset
        self.multiplexor_signal = multiplexor_signal
        self.multiplex_dependent = multiplex_dependent
        self.multiplexor_value = multiplexor_value


class Message(Base, RidMixIn, CommentableMixIn):

    name = Column(types.Unicode(255), nullable = True, index = True)
    message_id = StdInteger(nullable = True, default = None)
    dlc = StdInteger()
    sender = StdInteger()

    #transmitter_node_id

    type = Column(types.String(256))

    message_signals = relationship(
        "Message_Signal", cascade="all, delete-orphan", backref="message"
    )
    signals = association_proxy("message_signals", "signal")

    __mapper_args__ = {
        "polymorphic_identity": "Message",
        "polymorphic_on": type,
    }


class Signal(Base, RidMixIn, CommentableMixIn):
    """

    """
    name = Column(types.Unicode(255), nullable = False, index = True)
    bitsize = StdInteger()
    byteorder = StdInteger(default = 1)
    sign = StdInteger(default = 1)
    valuetype = StdInteger(default = 0)
    formula_factor = Column(types.Float, default = 1.0)
    formula_offset = Column(types.Float, default = 0.0)
    minimum = Column(types.Float, default = 0.0)
    maximum = Column(types.Float, default = 0.0)
    unit = Column(types.Unicode(255))
    type = Column(types.String(256))

    __mapper_args__ = {
        "polymorphic_identity": "Signal",
        "polymorphic_on": type,
    }


class Network(Base, RidMixIn, CommentableMixIn):
    """
    """

    name = Column(types.Unicode(255), nullable = False, unique = True, index = True)
    protocol = StdInteger()
    baudrate = StdInteger()
    type = Column(types.String(256))
    __mapper_args__ = {
        "polymorphic_identity": "Network",
        "polymorphic_on": type,
    }


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

    node_id = Column(types.Integer,
        ForeignKey("node.rid", onupdate = "CASCADE", ondelete = "RESTRICT"),
        nullable = False, default = 0, primary_key = True
    )
    message_id = Column(types.Integer,
        ForeignKey("message.rid", onupdate = "CASCADE", ondelete = "RESTRICT"),
        nullable = False, default = 0, primary_key = True
    )
    signal_id = Column(types.Integer,
        ForeignKey("signal.rid", onupdate = "CASCADE", ondelete = "RESTRICT"),
        nullable = False, default = 0, primary_key = True
    )
    __table_args__ = (
        ForeignKeyConstraint(columns = ["message_id", "signal_id"],
            refcolumns = ["message_signal.message_id", "message_signal.signal_id"]
        ),
    )

    #receiver_id = relationship(
    #    "Node_RxSignal", cascade="all, delete-orphan", backref="signal"
    #)
    #receiver = association_proxy("receiver_id", "signal")

    node = relationship("Node", uselist  = False, lazy = "joined")
    message = relationship("Message", uselist  = False, lazy = "joined")
    signal = relationship("Signal", uselist  = False, lazy = "joined")    # backref = "rx_signals", uselist  = False,


class Node_TxMessage(Base, MixInBase):

    node_id = Column(types.Integer,
        ForeignKey("node.rid", onupdate = "CASCADE", ondelete = "RESTRICT"),
        nullable = False, default = 0, primary_key = True
    )
    message_id = Column(types.Integer,
        ForeignKey("message.rid", onupdate = "CASCADE", ondelete = "RESTRICT"),
        nullable = False, default = 0, primary_key = True
    )
    node = relationship("Node", backref = "tx_messages", uselist  = False)
    message = relationship("Message", backref = "tx_messages", uselist  = False)

class Node_TxSig(Base, MixInBase):

    node_id = Column(types.Integer,
        ForeignKey("node.rid", onupdate = "CASCADE", ondelete = "RESTRICT"),
        nullable = False, default = 0, primary_key = True
    )
    signal_id = Column(types.Integer,
        ForeignKey("signal.rid", onupdate = "CASCADE", ondelete = "RESTRICT"),
        nullable = False, default = 0, primary_key = True
    )
    node = relationship("Node", backref = "tx_sigs", uselist  = False)
    signal = relationship("Signal", backref = "tx_sigs", uselist  = False)

class Attribute_Definition(Base, RidMixIn, CommentableMixIn):

    name = Column(types.Unicode(255), nullable = False, unique = True, index = True)
    objecttype = StdInteger()
    valuetype = StdInteger()
    array = Column(types.Boolean, default = False)
    minimum = Column(types.Float, default = 0.0)
    maximum = Column(types.Float, default = 0.0)
    enumvalues = Column(types.TEXT)
    default_number = Column(types.Float, default = 0.0)
    default_string = Column(types.Unicode(255), default = None)

class Attribute_Value(Base, MixInBase):

    object_id = Column(types.Integer, nullable = False, default = 0, primary_key = True)
    attribute_definition_id = Column(types.Integer,
        ForeignKey("attribute_definition.rid", onupdate = "CASCADE", ondelete = "RESTRICT"),
        nullable = False, default = 0, primary_key = True,
    )
    num_value = Column(types.Float, default = 0.0)
    string_value = Column(types.TEXT)
    attribute_definition = relationship("Attribute_Definition", backref = "values")

    """
    @hybrid_property
    def value(self):
        return self.num_value

    @value.setter
    def value(self, v):
        print("Setting value to '{}'".format(v))

    @value.expression
    def value(self):
        return self.num_value
    """


class AttributeRel_Value(Base, MixInBase):

    object_id = Column(types.Integer, nullable = False, default = 0, primary_key = True)
    attribute_definition_id = Column(types.Integer,
        ForeignKey("attribute_definition.rid", onupdate = "CASCADE", ondelete = "RESTRICT"),
        nullable = False, default = 0, primary_key = True,
    )
    num_value = Column(types.Float, default = 0.0)
    string_value = Column(types.TEXT)
    opt_object_id_1 = Column(types.Integer, nullable = False, default = 0, primary_key = True)
    opt_object_id_2 = Column(types.Integer, nullable = False, default = 0, primary_key = True)
    blob_value = Column(types.BLOB)
    attribute_definition = relationship("Attribute_Definition", backref = "attribute_rel_values")


class Vndb_Meta(Base, RidMixIn):

    schema_version = StdInteger()
    vndb_type = StdInteger()
    created = Column(types.DateTime, default = datetime.datetime.now)


class Vndb_Migrations(Base, RidMixIn):

    app = Column(types.Unicode(255), nullable = False)
    name = Column(types.Unicode(255), nullable = False)
    applied = Column(types.DateTime,  func.now)


class Vndb_Protocol(Base, MixInBase):

    network_id = Column(types.Integer,
        ForeignKey("network.rid", onupdate = "CASCADE", ondelete = "RESTRICT"),
        nullable = False, default = 0, primary_key = True,
    )
    name = Column(types.Unicode(255), nullable = False)
    specific = Column(types.Unicode(255), nullable = True)
    network = relationship("Network", uselist = False)

class ECU(Base, RidMixIn, CommentableMixIn):

    name = Column(types.Unicode(255), nullable = False, unique = True, index = True)


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


class Signal_Group(Base, RidMixIn):

    name = Column(types.Unicode(255), nullable = False)
    value = Column(types.Integer, nullable = False, default = 0)
    message_id = Column(types.Integer,
        ForeignKey("message.rid", onupdate = "CASCADE", ondelete = "RESTRICT"),
        nullable = False, default = 0
    )
    message = relationship("Message", backref = "signal_groups")
    UniqueConstraint("Message", "Name")


class Signal_Group_Signal(Base, MixInBase):

    signal_group_id = Column(types.Integer,
        ForeignKey("signal_group.rid", onupdate = "CASCADE", ondelete = "RESTRICT"),
        nullable = False, default = 0, primary_key = True
    )
    message_id = Column(types.Integer,
        ForeignKey("message.rid", onupdate = "CASCADE", ondelete = "RESTRICT"),
        nullable = False, default = 0, primary_key = True
    )
    signal_id = Column(types.Integer,
        ForeignKey("signal.rid", onupdate = "CASCADE", ondelete = "RESTRICT"),
        nullable = False, default = 0, primary_key = True
    )
    signal_group = relationship("Signal_Group", backref = "signal_group_signal")
    message = relationship("Message", backref = "signal_group_signal")
    signal = relationship("Signal", backref = "signal_group_signal")


class Valuetable(Base, RidMixIn, CommentableMixIn):
    """
    """
    name = Column(types.Unicode(255), nullable = False, index = True)


class Object_Valuetable(Base, MixInBase):
    """

    """
    object_type = Column(types.Integer, nullable = False, default = 0)  # , primary_key = True
    object_rid = Column(types.Integer, nullable = False, default = 0)   # , primary_key = True
    valuetable_id = Column(types.Integer,
        ForeignKey("valuetable.rid", onupdate = "CASCADE", ondelete = "RESTRICT"),
        nullable = False, default = 0, primary_key = True
    )
    valuetable = relationship("Valuetable", backref = "object_valuetable", uselist = False)


class Value_Description(Base, MixInBase):

    valuetable_id = Column(types.Integer,
        ForeignKey("valuetable.rid", onupdate = "CASCADE", ondelete = "RESTRICT"),
        nullable = False, default = 0, primary_key = True
    )
    value = Column(types.Float, nullable = False, default = 0.0, primary_key = True)
    value_description = Column(types.Unicode(255), nullable = False)
    valuetable = relationship("Valuetable", backref = "values")


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

    object_type = Column(types.Integer, nullable = False, default = 0, primary_key = True)
    object_rid = Column(types.Integer, nullable = False, default = 0, primary_key = True)
    version_number = Column(types.Integer, nullable = False, default = 0)
    is_modified = Column(types.Boolean, nullable = False, default = False)


class Category_Definition(Base, RidMixIn):

    name = Column(types.Unicode(255), nullable = False)
    key = Column(types.Integer, nullable = False, default = 0, unique = True)
    level = Column(types.Integer, nullable = False, default = 0)


class Category_Value(Base, MixInBase):

    object_id = Column(types.Integer, nullable = False, default = 0, primary_key = True)
    category_definition_id = Column(types.Integer,
        ForeignKey("category_definition.key", onupdate = "CASCADE", ondelete = "RESTRICT"),
        nullable = False, default = 0
    )
    objecttype = Column(types.Integer, nullable = False, default = 0, primary_key = True)
    category_definition = relationship("Category_Definition", backref = "values")

class Dbc_Version(Base, RidMixIn):

    version_string = Column(types.Unicode(255), nullable = False, default = '')
    network = Column(types.Integer, nullable = False, default = 0, unique = True)


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

##
##  LIN specific classses.
##
class LinNetwork(Network):
    """

    """
    lin_network_id = Column(
        types.Integer,
        ForeignKey("network.rid"),
        primary_key = True
    )
    __mapper_args__ = {
        "polymorphic_identity": "LinNetwork"
    }

    protocol_version = Column(types.Unicode(255), nullable = True, default = None)
    language_version = Column(types.Unicode(255), nullable = True, default = None)
    file_revision = Column(types.Unicode(255), nullable = True, default = None)
    speed = StdFloat(default = None, nullable = True)
    channel_name = Column(types.Unicode(255), nullable = True, default = None)

    def __init__(self, name, protocol_version = None, language_version = None, speed = None,
                 file_revision = None, channel_name = None):
        self.name = name
        self.protocol_version = protocol_version
        self.language_version = language_version
        self.file_revision = file_revision
        self.speed = speed
        self.channel_name = channel_name

    def __str__(self):
        return 'LinNetwork(name = "{}", protocol_version = "{}", language_version = "{}",'\
            'file_revision = "{}", speed = {}, channel_name = "{}")'.format(self.name, self.protocol_version,
            self.language_version, self.file_revision or "", self.speed, self.channel_name or ""
        )

    __repr__ = __str__


class LinNode(Node):
    """
    """
    lin_node_id = Column(
        types.Integer,
        ForeignKey("node.rid"),
        primary_key = True
    )

    __mapper_args__ = {
        "polymorphic_identity": "LinNode"
    }


class LinMasterNode(LinNode):
    """
    """
    lin_master_node_id = Column(
        types.Integer,
        ForeignKey("linnode.lin_node_id"),
        primary_key = True
    )

    timebase = StdFloat(default = 0.0)
    jitter = StdFloat(default = 0.0)

    # Only J2602.
    bit_length = StdInteger(nullable = True, default = None)
    tolerant = StdFloat(nullable = True, default = None)

    __mapper_args__ = {
        "polymorphic_identity": "LinMasterNode"
    }

    def __init__(self, name, timebase, jitter, bit_length = None, tolerant = None):
        self.name = name
        self.timebase = timebase
        self.jitter = jitter
        self.bit_length = bit_length
        self.tolerant = tolerant

    def __repr__(self):
        return 'LinMasterNode(name = "{}", timebase = {}, jitter = {}, bit_length = {}, tolerant = {})'.format(self.name,
            self.timebase, self.jitter, self.bit_length, self.tolerant
        )

    __str__ = __repr__


class LinSlaveNode(LinNode):
    """
    """
    lin_slave_node_id = Column(
        types.Integer,
        ForeignKey("linnode.lin_node_id"),
        primary_key = True
    )

    protocol_version = Column(types.Unicode(255))
    configured_NAD = StdInteger(nullable = True, default = None)
    initial_NAD = StdInteger(nullable = True, default = None)

    supplier_id = StdInteger(default = 0)
    function_id = StdInteger(default = 0)
    variant = StdInteger(nullable = True, default = None)

    p2_min = StdFloat(nullable = True, default = None)
    st_min = StdFloat(nullable = True, default = None)
    n_as_timeout = StdFloat(nullable = True, default = None)
    n_cr_timeout = StdFloat(nullable = True, default = None)
    response_tolerance = StdFloat(nullable = True, default = None)

    @hybrid_property
    def product_id(self):
        return LinProductIdType(self.supplier_id, self.function_id, self.variant)

    @product_id.setter
    def product_id(self, product_id):
        """
        """
        if product_id in ("", ()):
            self.supplier_id = self.function_id = self.variant = 0
        elif isinstance(product_id, LinProductIdType):
            self.supplier_id = product_id.supplier_id
            self.function_id = product_id.function_id
            self.variant = product_id.variant
        elif isinstance(product_id, str):
            parts = product_id.split(".")
            self.supplier_id, self.function_id, self.variant = [int(c) for c in parts]
        elif isinstance(product_id, tuple):
            if len(product_id) != 3:
                raise ValueError("product_id as tuple must contain three elements: (supplier_id, function_id, variant)")
            else:
                supplier_id, function_id, variant = product_id
                self.supplier_id = int(supplier_id)
                self.function_id = int(function_id)
                self.variant = int(variant)
        else:
            raise TypeError("product_id must be LinProductIdType, string, or 3-tuple.")

    __mapper_args__ = {
        "polymorphic_identity": "LinSlaveNode"
    }

    def __init__(self, name, protocol_version = None, configured_NAD = None, initial_NAD = None, product_id = (),
                 p2_min = None, st_min = None, n_as_timeout = None, n_cr_timeout = None, response_tolerance = None):
        self.name = name
        self.protocol_version = protocol_version
        self.configured_NAD = configured_NAD
        self.initial_NAD = initial_NAD
        self.product_id = product_id
        self.p2_min = p2_min
        self.st_min = st_min
        self.n_as_timeout = n_as_timeout
        self.n_cr_timeout = n_cr_timeout
        self.response_tolerance = response_tolerance

    def __repr__(self):
        return 'LinSlaveNode(name = "{}", protocol_version = "{}", configured_NAD = {}, initial_NAD = {}, product_id = {}, p2_min = {}, st_min = {}, n_as_timeout = {}, n_cr_timeout = {}, response_tolerance = {})'.format(
            self.name, self.protocol_version, self.configured_NAD, self.initial_NAD, self.product_id,
            self.p2_min, self.st_min, self.n_as_timeout, self.n_cr_timeout, self.response_tolerance
        )

    __str__ = __repr__




class LinSignal(Signal):
    """

    """
    lin_signal_id = Column(
        types.Integer,
        ForeignKey("signal.rid"),
        primary_key = True
    )
    _init_value = Column(types.Unicode(255), default = "0")

    publisher_id =  Column(types.Integer,
        ForeignKey("linnode.lin_node_id", onupdate = "CASCADE", ondelete = "RESTRICT"),
        nullable = False
    )
    publisher = relationship("LinNode", backref = "signals")

    signal_subscribers = relationship(
        "LinSignalSubscriber", cascade="all, delete-orphan", backref="signal"
    )
    subscribers = association_proxy("signal_subscribers", "subscriber")

    __mapper_args__ = {
        "polymorphic_identity": "LinSignal"
    }

    def __init__(self, name, signal_size, init_value, publisher):
        self.name = name
        self.bitsize = signal_size
        self.byteorder = ByteOrderType.MOTOROLA
        self.valuetype = ValueType.INT
        self.init_value = init_value
        self.publisher = publisher

    @hybrid_property
    def init_value(self):
        value = self._init_value
        match = INIT_VALUE.match(value)
        if match:
            gd = match.groupdict()
            if gd['array']:
                value = [int(v) for v in value.split(",")]
            else:
                value = int(value)
        else:
            raise ValueError("Malformed initial value '{}'.".format(value))
        return value

    @init_value.setter
    def init_value(self, value):
        if isinstance(value, int):
            value = str(value)
        elif isinstance(value, (list, tuple)):
            value = ','.join([str(x) for x in value])
        self._init_value = value

    def __str__(self):
        return 'LinSignal(name = "{}", signal_size = {}, init_value = {})'.format(self.name, self.bitsize, self.init_value)

    __repr__ = __str__


class LinSignalSubscriber(Base, MixInBase):
    """

    """
    lin_node_id = Column(types.Integer,
        ForeignKey("linnode.lin_node_id", onupdate = "CASCADE", ondelete = "RESTRICT"),
        nullable = False, primary_key = True
    )
    lin_signal_id = Column(types.Integer,
        ForeignKey("linsignal.lin_signal_id", onupdate = "CASCADE", ondelete = "RESTRICT"),
        nullable = False, primary_key = True
    )
    subscriber = relationship(LinNode, lazy = "joined")

    def __init__(self, subscriber):
        self.subscriber = subscriber


class LinUnconditionalFrame(Message):
    """
    """
    lin_unconditional_frame_id = Column(
        types.Integer,
        ForeignKey("message.rid"),
        primary_key = True
    )

    frame_signals = relationship(
        "LinUnconditionalFrameSignal", cascade="all, delete-orphan", backref="frame"
    )
    signals = association_proxy("frame_signals", "signal")

    publisher_id =  Column(types.Integer,
        ForeignKey("linnode.lin_node_id", onupdate = "CASCADE", ondelete = "RESTRICT"),
        nullable = False
    )
    publisher = relationship("LinNode", backref = "unconditional_frames")

    __mapper_args__ = {
        "polymorphic_identity": "LinUnconditionalFrame"
    }

    def __init__(self, name, frame_id, size, publisher):
        self.name = name
        self.size = size
        self.frame_id = frame_id
        self.publisher = publisher

    def __repr__(self):
        return 'LinUnconditionalFrame(name = "{}", frame_id = {}, size = {}, publisher = {})'.format(
            self.name, self.frame_id, self.size, self.publisher
        )

    __str__ = __repr__

    @hybrid_property
    def size(self):
        return self.dlc

    @size.setter
    def size(self, value):
        if not (1 <= value <= 8):
            raise ValueError("'size' must be in range [1 .. 8]")
        self.dlc = value

    @hybrid_property
    def frame_id(self):
        return self.message_id

    @frame_id.setter
    def frame_id(self, value):
        if not (0 <= value <= 59):
            raise ValueError("'frame_id' must be in range [0 .. 59]")
        self.message_id = value

    def add_signal(self, signal, signal_offset):
        return self.frame_signals.append(LinUnconditionalFrameSignal(signal, signal_offset))


class LinUnconditionalFrameSignal(Base, MixInBase):
    """

    """
    lin_unconditional_frame_id = Column(
        types.Integer,
        ForeignKey("linunconditionalframe.lin_unconditional_frame_id"),
        primary_key = True
    )

    lin_signal_id = Column(types.Integer,
        ForeignKey("linsignal.lin_signal_id", onupdate = "CASCADE", ondelete = "RESTRICT"),
        nullable = False, primary_key = True
    )
    signal_offset = StdInteger(default = 0)
    unconditional_frame = relationship(LinUnconditionalFrame, lazy = "joined")
    signal = relationship(LinSignal, lazy = "joined")

    def __init__(self, signal, signal_offset = 0):
        self.signal = signal
        self.signal_offset = signal_offset

    def __repr__(self):
        return 'LinUnconditionalFrameSignal(unconditional_frame = {}, signal = {}, signal_offset = {})'.format(
            self.unconditional_frame, self.signal, self.signal_offset
        )
    __str__ = __repr__


class LinSignalEncodingType(Base, RidMixIn):
    """
    """
    name = Column(types.Unicode(255), nullable = False, unique = True)

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return 'LinSignalEncodingType(name = "{}")'.format(self.name)

    __str__ = __repr__


class LinSignalRepresentation(Base, MixInBase):
    """
    """
    lin_signal_encoding_type_id = Column(types.Integer,
        ForeignKey("linsignalencodingtype.rid"),
        nullable = False, primary_key = True
    )
    signal_id = Column(types.Integer,
        ForeignKey("signal.rid", onupdate = "CASCADE", ondelete = "RESTRICT"),
        nullable = False, default = 0, primary_key = True
    )
    signal_encoding_type = relationship("LinSignalEncodingType", backref = "representations", uselist = False)
    signal = relationship("Signal",  uselist  = False)

    def __init__(self, signal_encoding_type, signal):
        self.signal_encoding_type = signal_encoding_type
        self.signal = signal

    def __repr__(self):
        return 'LinSignalRepresentation(signal_encoding_type = {}, signal = {})'.format(self.signal_encoding_type, self.signal)

    __str__ = __repr__


class LinSignalEncodingEntry(Base, MixInBase):

    entry_id = Column(types.Integer, primary_key = True)

    lin_signal_encoding_type_id = Column(types.Integer,
        ForeignKey("linsignalencodingtype.rid"),
        nullable = False, # , primary_key = True
    )
    type = Column(types.String(75))
    signal_encoding_type = relationship("LinSignalEncodingType", backref = "entries", uselist = False)

    __mapper_args__ = {
        "polymorphic_identity": "LinSignalEncodingEntry",
        "polymorphic_on": type,
    }


class LinSignalEncodingEntry_Value(LinSignalEncodingEntry):

    entry_id = Column(
        types.Integer,
        ForeignKey("linsignalencodingentry.entry_id"),
        primary_key = True
    )
    entry_type = Column(types.Integer)

    __mapper_args__ = {
        "polymorphic_identity": "LinSignalEncodingEntry_Value"
    }

    def __init__(self, entry_type):
        self.entry_type = entry_type

    def __repr__(self):
        return 'LinSignalEncodingEntry_Value(entry_type = {})'.format(self.entry_type)

    __str__ = __repr__


class LinSignalEncodingEntry_Logical(LinSignalEncodingEntry):

    entry_id = Column(
        types.Integer,
        ForeignKey("linsignalencodingentry.entry_id"),
        primary_key = True
    )
    signal_value = Column(types.Float, nullable = False)
    text_info = Column(types.Unicode(1024), nullable = True)

    __mapper_args__ = {
        "polymorphic_identity": "LinSignalEncodingEntry_Logical"
    }

    def __init__(self, signal_value, text_info):
        self.signal_value = signal_value
        self.text_info = text_info

    def __repr__(self):
        return 'LinSignalEncodingEntry_Logical(signal_value = {}, text_info = "{}")'.format(self.signal_value, self.text_info)

    __str__ = __repr__


class LinSignalEncodingEntry_Physical(LinSignalEncodingEntry):

    entry_id = Column(
        types.Integer,
        ForeignKey("linsignalencodingentry.entry_id"),
        primary_key = True
    )
    min_value = Column(types.Float, nullable = False)
    max_value = Column(types.Float, nullable = False)
    scale = Column(types.Float, nullable = False)
    offset = Column(types.Float, nullable = False)
    text_info = Column(types.Unicode(1024), nullable = True)

    __mapper_args__ = {
        "polymorphic_identity": "LinSignalEncodingEntry_Physical"
    }

    def __init__(self, min_value, max_value, scale, offset, text_info):
        min_value, max_value, scale, offset, text_info

    def __repr__(self):
        return 'LinSignalEncodingEntry_Physical(min_value = {}, max_value = {}, scale = {}, offset = {}, text_info = "{}")'.format(
            self.min_value, self.max_value, self.scale, self.offset, self.text_info
        )

    __str__ = __repr__


class LinScheduleTable(Base, RidMixIn):
    """
    """

    name = Column(types.Unicode(255), nullable = False, unique = True)
    entries = relationship("LinScheduleTable_Command", order_by="LinScheduleTable_Command.position",
                           collection_class = ordering_list('position')
    )


class LinScheduleTable_Command(Base, MixInBase):
    """
    """
    command_id = Column(types.Integer, primary_key = True)

    lin_schedule_table_id = Column(types.Integer,
        ForeignKey("linscheduletable.rid"),
        nullable = False, # , primary_key = True
    )
    frame_time = Column(types.Float, nullable = False)
    type = Column(types.String(75))
    position = StdInteger()

    __mapper_args__ = {
        "polymorphic_identity": "LinScheduleTable_Command",
        "polymorphic_on": type,
    }

    def __init__(self, frame_time):
        self.frame_time = frame_time

    def __repr__(self):
        return 'LinScheduleTable_Command(frame_time = {})'.format(self.frame_time)

    __str__ = __repr__


class LinScheduleTable_Command_Frame(LinScheduleTable_Command):
    """
    """
    command_id = Column(
        types.Integer,
        ForeignKey("linscheduletable_command.command_id"),
        primary_key = True
    )
    frame_id = Column(types.Integer,
        ForeignKey("linunconditionalframe.lin_unconditional_frame_id"),
        nullable = False, default = 0, primary_key = True
    )
    frame = relationship("LinUnconditionalFrame", backref = "entries", uselist = False)

    __mapper_args__ = {"polymorphic_identity": "LinScheduleTable_Command_Frame"}

    def __init__(self, frame_time, frame):
        self.frame_time = frame_time
        self.frame = frame

    def __repr__(self):
        return 'LinScheduleTable_Command_Frame(frame_time = {}, frame = {})'.format(self.frame_time, self.frame)

    __str__ = __repr__


class LinScheduleTable_Command_MasterReq(LinScheduleTable_Command):
    """
    """
    command_id = Column(
        types.Integer,
        ForeignKey("linscheduletable_command.command_id"),
        primary_key = True
    )

    __mapper_args__ = {
        "polymorphic_identity": "LinScheduleTable_Command_MasterReq"
    }


    def __init__(self, frame_time):
        self.frame_time = frame_time

    def __repr__(self):
        return 'LinScheduleTable_Command_MasterReq(frame_time = {})'.format(self.frame_time)

    __str__ = __repr__


class LinScheduleTable_Command_SlaveResp(LinScheduleTable_Command):
    """
    """
    command_id = Column(
        types.Integer,
        ForeignKey("linscheduletable_command.command_id"),
        primary_key = True
    )

    __mapper_args__ = {
        "polymorphic_identity": "LinScheduleTable_Command_SlaveResp"
    }

    def __init__(self, frame_time):
        self.frame_time = frame_time

    def __repr__(self):
        return 'LinScheduleTable_Command_SlaveResp(frame_time = {})'.format(self.frame_time)

    __str__ = __repr__


class LinScheduleTable_Command_AssignNad(LinScheduleTable_Command):
    """
    """
    command_id = Column(
        types.Integer,
        ForeignKey("linscheduletable_command.command_id"),
        primary_key = True
    )
    node_id = Column(types.Integer,
        ForeignKey("node.rid", onupdate = "CASCADE", ondelete = "RESTRICT"),
        nullable = False, default = 0, primary_key = True
    )
    node = relationship("Node", backref = "assign_nads", uselist  = False)

    __mapper_args__ = {
        "polymorphic_identity": "LinScheduleTable_Command_AssignNad"
    }

    def __init__(self, frame_time, node):
        self.frame_time = frame_time
        self.node = node

    def __repr__(self):
        return 'LinScheduleTable_Command_AssignNad(frame_time = {}, node = {})'.format(self.frame_time, self.node)

    __str__ = __repr__


class LinScheduleTable_Command_ConditionalChangeNad(LinScheduleTable_Command):
    """
    """
    command_id = Column(
        types.Integer,
        ForeignKey("linscheduletable_command.command_id"),
        primary_key = True
    )
    nad = Column(types.Integer)
    id = Column(types.Integer)
    byte = Column(types.Integer)
    mask = Column(types.Integer)
    inv = Column(types.Integer)
    new_nad = Column(types.Integer)

    __mapper_args__ = {
        "polymorphic_identity": "LinScheduleTable_Command_ConditionalChangeNad"
    }

    def __init__(self, frame_time, nad, id, byte, mask , inv, new_nad):
        self.frame_time = frame_time
        self.nad = nad
        self.id = id
        self.byte = byte
        self.mask = mask
        self.inv = inv
        self.new_nad = new_nad

    def __repr__(self):
        return 'LinScheduleTable_Command_ConditionalChangeNad(frame_time = {}, nad = {}, id = {}, byte = {}, mask = {}, inv = {}, new_nad = {})'.format(
            self.frame_time, self.nad, self.id, self.byte, self.mask, self.inv, self.new_nad
    )

    __str__ = __repr__


class LinScheduleTable_Command_DataDump(LinScheduleTable_Command):
    """
    """
    command_id = Column(
        types.Integer,
        ForeignKey("linscheduletable_command.command_id"),
        primary_key = True
    )
    node_id = Column(types.Integer,
        ForeignKey("node.rid", onupdate = "CASCADE", ondelete = "RESTRICT"),
        nullable = False, default = 0, primary_key = True
    )
    node = relationship("Node", backref = "data_dumps", uselist  = False)
    d1 = Column(types.Integer)
    d2 = Column(types.Integer)
    d3 = Column(types.Integer)
    d4 = Column(types.Integer)
    d5 = Column(types.Integer)

    __mapper_args__ = {
        "polymorphic_identity": "LinScheduleTable_Command_DataDump"
    }

    def __init__(self, frame_time, node, d1, d2, d3, d4, d5):
        self.frame_time = frame_time
        self.node = node
        self.d1 = d1
        self.d2 = d2
        self.d3 = d3
        self.d4 = d4
        self.d5 = d5

    def __repr__(self):
        return 'LinScheduleTable_Command_DataDump(frame_time = {}, node = {}, d1 = {}, d2 = {}, d3 = {}, d4 = {}, d5 = {})'.format(
            self.frame_time, self.node, self.d1, self.d2, self.d3, self.d4, self.d5
        )

    __str__ = __repr__


class LinScheduleTable_Command_SaveConfiguration(LinScheduleTable_Command):
    """
    """
    command_id = Column(
        types.Integer,
        ForeignKey("linscheduletable_command.command_id"),
        primary_key = True
    )
    node_id = Column(types.Integer,
        ForeignKey("node.rid", onupdate = "CASCADE", ondelete = "RESTRICT"),
        nullable = False, default = 0, primary_key = True
    )
    node = relationship("Node", backref = "save_configurations", uselist  = False)

    __mapper_args__ = {
        "polymorphic_identity": "LinScheduleTable_Command_SaveConfiguration"
    }

    def __init__(self, frame_time, node):
        self.frame_time = frame_time
        self.node = node

    def __repr__(self):
        return 'LinScheduleTable_Command_SaveConfiguration(frame_time = {}, node = {})'.format(self.frame_time, self.node)

    __str__ = __repr__


class LinScheduleTable_Command_AssignFrameIdRange(LinScheduleTable_Command):
    """
    """
    command_id = Column(
        types.Integer,
        ForeignKey("linscheduletable_command.command_id"),
        primary_key = True
    )
    node_id = Column(types.Integer,
        ForeignKey("node.rid", onupdate = "CASCADE", ondelete = "RESTRICT"),
        nullable = False, default = 0, primary_key = True
    )
    node = relationship("Node", backref = "assign_frame_id_ranges", uselist  = False)
    frame_index = Column(types.Integer)
    frame_pid1 = Column(types.Integer)
    frame_pid2 = Column(types.Integer)
    frame_pid3 = Column(types.Integer)
    frame_pid4 = Column(types.Integer)

    __mapper_args__ = {
        "polymorphic_identity": "LinScheduleTable_Command_AssignFrameIdRange"
    }

    def __init__(self, frame_time, node, frame_index, frame_pid1 = None, frame_pid2 = None, frame_pid3 = None, frame_pid4 = None):
        self.frame_time = frame_time
        self.node = node
        self.frame_index = frame_index
        self.frame_pid1 = frame_pid1
        self.frame_pid2 = frame_pid2
        self.frame_pid3 = frame_pid3
        self.frame_pid4 = frame_pid4

    def __repr__(self):
        return 'LinScheduleTable_Command_AssignFrameIdRange(frame_time = {}, node = {}, frame_index = {}, frame_pid1 = {}, frame_pid2 = {}, frame_pid3 = {}, frame_pid4 = {})'.format(
            self.frame_time, self.node, self.frame_index, self.frame_pid1, self.frame_pid2, self.frame_pid3, self.frame_pid4
        )

    __str__ = __repr__


class LinScheduleTable_Command_FreeFormat(LinScheduleTable_Command):
    """
    """
    command_id = Column(
        types.Integer,
        ForeignKey("linscheduletable_command.command_id"),
        primary_key = True
    )
    d1 = Column(types.Integer)
    d2 = Column(types.Integer)
    d3 = Column(types.Integer)
    d4 = Column(types.Integer)
    d5 = Column(types.Integer)
    d6 = Column(types.Integer)
    d7 = Column(types.Integer)
    d8 = Column(types.Integer)

    __mapper_args__ = {
        "polymorphic_identity": "LinScheduleTable_Command_FreeFormat"
    }


    def __init__(self, frame_time, d1, d2, d3, d4, d5, d6, d7, d8):
        self.frame_time = frame_time
        self.d1 = d1
        self.d2 = d2
        self.d3 = d3
        self.d4 = d4
        self.d5 = d5
        self.d6 = d6
        self.d7 = d7
        self.d8 = d8

    def __repr__(self):
        return 'LinScheduleTable_Command_FreeFormat(frame_time = {}, d1 = {}, d2 = {}, d3 = {}, d4 = {}, d5 = {}, d6 = {}, d7 = {}, d8 = {})'.format(
            self.frame_time, self.d1, self.d2, self.d3, self.d4, self.d5, self.d6, self.d7, self.d8
        )

    __str__ = __repr__


class LinScheduleTable_Command_AssignFrameId(LinScheduleTable_Command):
    """
    """
    command_id = Column(
        types.Integer,
        ForeignKey("linscheduletable_command.command_id"),
        primary_key = True
    )
    node_id = Column(types.Integer,
        ForeignKey("node.rid", onupdate = "CASCADE", ondelete = "RESTRICT"),
        nullable = False, default = 0, primary_key = True
    )
    node = relationship("Node", backref = "assign_frame_ids", uselist  = False)
    frame_id = Column(types.Integer,
        ForeignKey("linunconditionalframe.lin_unconditional_frame_id"),
        nullable = False, default = 0, primary_key = True
    )
    frame = relationship("LinUnconditionalFrame", backref = "assign_frame_ids", uselist = False)

    __mapper_args__ = {"polymorphic_identity": "LinScheduleTable_Command_AssignFrameId"}

    def __init__(self, frame_time, node, frame):
        self.frame_time = frame_time
        self.node = node
        self.frame = frame

    def __repr__(self):
        return 'LinScheduleTable_Command_AssignFrameId(frame_time = {}, node = {}, frame = {})'.format(
            self.frame_time, self.node, self.frame)

    __str__ = __repr__



class LinSporadicFrame_Association(Base, MixInBase):
    """
    """
    sporadic_frame_id = Column(
        types.Integer,
        ForeignKey("linsporadicframe.frame_id"),
        primary_key = True
    )
    frame_id = Column(
        types.Integer,
        ForeignKey("linunconditionalframe.lin_unconditional_frame_id"),
        primary_key = True
    )
    unconditional_frame = relationship("LinUnconditionalFrame")
    position = StdInteger()

    def __init__(self, unconditional_frame):
        self.unconditional_frame = unconditional_frame


class LinSporadicFrame(LinUnconditionalFrame):
    """
    """
    frame_id = Column(
        types.Integer,
        ForeignKey("linunconditionalframe.lin_unconditional_frame_id"),
        primary_key = True
    )
    associated_frames = relationship("LinUnconditionalFrame", secondary = "linsporadicframe_association", uselist = True)

    """
    message_signals = relationship(
        "Message_Signal", cascade="all, delete-orphan", backref="message"
    )
    signals = association_proxy("message_signals", "signal")
    """

    __mapper_args__ = {
        "polymorphic_identity": "LinSporadicFrame"
    }

    def __init__(self, name):
        self.name = name


class LinEventTriggeredFrame_Association(Base, MixInBase):
    """
    """
    event_triggered_id = Column(
        types.Integer,
        ForeignKey("lineventtriggeredframe.frame_id"),
        primary_key = True
    )
    frame_id = Column(
        types.Integer,
        ForeignKey("linunconditionalframe.lin_unconditional_frame_id"),
        primary_key = True
    )
    event_triggered_frame = relationship("LinEventTriggeredFrame", foreign_keys = [event_triggered_id])
    unconditional_frame = relationship("LinUnconditionalFrame")
    #position = StdInteger()

    def __init__(self, unconditional_frame):
        self.unconditional_frame = unconditional_frame


class LinEventTriggeredFrame(LinUnconditionalFrame):
    """
    """
    frame_id = Column(
        types.Integer,
        ForeignKey("linunconditionalframe.lin_unconditional_frame_id"),
        primary_key = True
    )
    collision_resolving_schedule_table_id = Column(
        types.Integer,
        ForeignKey("linscheduletable.rid"),
        nullable = True,
    )

    collision_resolving_schedule_table = relationship("LinScheduleTable", backref = "event_triggered_frames",
        uselist = False
    )

    associated_frames = relationship("LinUnconditionalFrame", secondary = "lineventtriggeredframe_association",
        order_by = "LinEventTriggeredFrame_Association.frame_id", #collection_class = ordering_list('position'),
        uselist = True
    )

    #associated_frames_assoc = relationship("LinEventTriggeredFrame_Association",
    #    order_by = "LinEventTriggeredFrame_Association.position", collection_class = ordering_list('position'),
    #    #backref = "event_triggered_frame"
    #)
    #associated_frames = association_proxy("associated_frames_assoc", "event_triggered_frame")

    __mapper_args__ = {
        "polymorphic_identity": "LinEventTriggeredFrame"
    }

    def __init__(self, name, frame_id, master_node, collision_resolving_schedule_table = None):
        self.name = name
        self.frame_id = frame_id
        self.publisher = master_node
        self.collision_resolving_schedule_table = collision_resolving_schedule_table


class LinConfigurableFrame(Base, MixInBase):
    """
    """
    node_id = Column(types.Integer,
        ForeignKey("node.rid"),
        nullable = False,
        primary_key = True
    )
    frame_id = Column(
        types.Integer,
        ForeignKey("linunconditionalframe.lin_unconditional_frame_id"),
        primary_key = True
    )
    identifier = StdInteger(nullable = True)

    node = relationship("Node", backref = "configurable_frames", uselist  = False)
    frame = relationship("LinUnconditionalFrame", backref = "configurable_frames", uselist = False)


class LinFaultStateSignal(Base, MixInBase):
    """
    """
    node_id = Column(types.Integer,
        ForeignKey("node.rid"),
        nullable = False,
        primary_key = True
    )
    signal_id = Column(types.Integer,
        ForeignKey("signal.rid", onupdate = "CASCADE", ondelete = "RESTRICT"),
        nullable = False, default = 0, primary_key = True
    )
    node = relationship("Node", backref = "fault_state_signals", uselist  = False)
    signal = relationship("Signal",  uselist  = False)

    def __init__(self, node, signal):
        self.node = node
        self.signal = signal

    def __str__(self):
        return 'LinFaultStateSignal(node = {}, signal = {})'.format(self.node, self.signal)

    __repr__ = __str__


class LinResponseErrorSignal(Base, MixInBase):
    """
    """

    node_id = Column(types.Integer,
        ForeignKey("linnode.lin_node_id"),
        nullable = False,
        primary_key = True
    )

    signal_id = Column(types.Integer,
        ForeignKey("linsignal.lin_signal_id"),
        nullable = True, primary_key = True
    )

    node = relationship("LinNode", backref = "response_error", uselist  = False)
    signal = relationship("LinSignal", uselist = False)

    def __init__(self, node, signal):
        self.node = node
        self.signal = signal

    def __str__(self):
        return 'LinNodeResponseError(node = {}, signal = {})'.format(self.node, self.signal)

    __repr__ = __str__
