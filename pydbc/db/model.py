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
from sqlalchemy.ext.associationproxy import association_proxy
#from sqlalchemy.engine import Engine
from sqlalchemy.orm import relationship, with_polymorphic

Base = declarative_base()

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

"""
    order_items = relationship(
        "OrderItem", cascade="all, delete-orphan", backref="order"
    )
"""
        
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
    message_id = StdInteger()
    dlc = StdInteger()
    sender = StdInteger()
    type = Column(types.String(256))

    __mapper_args__ = {
        "polymorphic_identity": "Message",
        "polymorphic_on": type,
    }


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
    array = Column(types.Boolean, default = False)
    minimum = Column(types.Float, default = 0.0)
    maximum = Column(types.Float, default = 0.0)
    enumvalues = Column(types.TEXT)
    default_number = Column(types.Float, default = 0.0)
    default_string = Column(types.Unicode(255))

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
    node = relationship("Node", backref = "rx_signals", uselist  = False)
    message = relationship("Message", backref = "rx_signals", uselist  = False)
    signal = relationship("Signal", backref = "rx_signals", uselist  = False)

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

    name = Column(types.Unicode(255), nullable = False, index = True)

class Object_Valuetable(Base, MixInBase):

    object_type = Column(types.Integer, nullable = False, default = 0, primary_key = True)
    object_rid = Column(types.Integer, nullable = False, default = 0, primary_key = True)
    valuetable_id = Column(types.Integer,
        ForeignKey("valuetable.rid", onupdate = "CASCADE", ondelete = "RESTRICT"),
        nullable = False, default = 0
    )
    valuetable = relationship("Valuetable") # , backref = "values"

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
class LinUnconditionalFrame(Message):
    """
    """
    frame_id = Column(
        types.Integer, 
        ForeignKey("message.rid"),
        primary_key = True
    )
    
    __mapper_args__ = {"polymorphic_identity": "LinUnconditionalFrame"}

    
class LinSignalEncodingType(Base, RidMixIn):
    """
    """
    name = Column(types.Unicode(255), nullable = False, unique = True)
    

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
    lin_signal_encoding_type = relationship("LinSignalEncodingType", backref = "representations", uselist = False)
    signal = relationship("Signal",  uselist  = False)


class LinSignalEncodingEntry(Base, MixInBase):

    entry_id = Column(types.Integer, primary_key = True)
    
    lin_signal_encoding_type_id = Column(types.Integer,
        ForeignKey("linsignalencodingtype.rid"), 
        nullable = False, # , primary_key = True
    )
    
    type = Column(types.String(75))
    lin_signal_encoding_type = relationship("LinSignalEncodingType", backref = "entries", uselist = False)

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

    __mapper_args__ = {"polymorphic_identity": "LinSignalEncodingEntry_Value"}


class LinSignalEncodingEntry_Logical(LinSignalEncodingEntry):
    
    entry_id = Column(
        types.Integer, 
        ForeignKey("linsignalencodingentry.entry_id"),
        primary_key = True
    )
    signal_value = Column(types.Float, nullable = False)
    text_info = Column(types.Unicode(1024), nullable = True)

    __mapper_args__ = {"polymorphic_identity": "LinSignalEncodingEntry_Logical"}
    

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

    __mapper_args__ = {"polymorphic_identity": "LinSignalEncodingEntry_Physical"}

    
class LinScheduleTable(Base, RidMixIn):
    """
    """
    name = Column(types.Unicode(255), nullable = False, unique = True)


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
    lin_schedule_table = relationship("LinScheduleTable", backref = "commands", uselist = False)

    __mapper_args__ = {
        "polymorphic_identity": "LinScheduleTable_Command",
        "polymorphic_on": type,
    }

    
class LinScheduleTable_Command_Frame(LinScheduleTable_Command):
    """
    """
    command_id = Column(
        types.Integer, 
        ForeignKey("linscheduletable_command.command_id"),
        primary_key = True
    )
    frame_id = Column(types.Integer,
        ForeignKey("linunconditionalframe.frame_id"),
        nullable = False, default = 0, primary_key = True
    )
    frame = relationship("LinUnconditionalFrame", backref = "commands", uselist = False)
    
    __mapper_args__ = {"polymorphic_identity": "LinScheduleTable_Command_Frame"}


class LinScheduleTable_Command_MasterReq(LinScheduleTable_Command):
    """
    """
    command_id = Column(
        types.Integer, 
        ForeignKey("linscheduletable_command.command_id"),
        primary_key = True
    )
    
    __mapper_args__ = {"polymorphic_identity": "LinScheduleTable_Command_MasterReq"}
    

class LinScheduleTable_Command_SlaveResp(LinScheduleTable_Command):
    """
    """
    command_id = Column(
        types.Integer, 
        ForeignKey("linscheduletable_command.command_id"),
        primary_key = True
    )
    
    __mapper_args__ = {"polymorphic_identity": "LinScheduleTable_Command_SlaveResp"}
    
    
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
    
    __mapper_args__ = {"polymorphic_identity": "LinScheduleTable_Command_AssignNad"}
    
    
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

    __mapper_args__ = {"polymorphic_identity": "LinScheduleTable_Command_ConditionalChangeNad"}
    
    
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
    
    __mapper_args__ = {"polymorphic_identity": "LinScheduleTable_Command_DataDump"}
    
    
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
    
    __mapper_args__ = {"polymorphic_identity": "LinScheduleTable_Command_SaveConfiguration"}
    
    
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
    
    __mapper_args__ = {"polymorphic_identity": "LinScheduleTable_Command_AssignFrameIdRange"}
    
    
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
    
    __mapper_args__ = {"polymorphic_identity": "LinScheduleTable_Command_FreeFormat"}
    
    
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
        ForeignKey("message.rid"),
        nullable = False, default = 0, primary_key = True
    )
    frame = relationship("Message", backref = "assign_frame_ids", uselist = False)
    
    __mapper_args__ = {"polymorphic_identity": "LinScheduleTable_Command_AssignFrameId"}

    
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
        ForeignKey("linunconditionalframe.frame_id"),
        primary_key = True
    )

    
class LinSporadicFrame(LinUnconditionalFrame):
    """
    """
    frame_id = Column(
        types.Integer, 
        ForeignKey("linunconditionalframe.frame_id"),
        primary_key = True
    )    
    associated_frames = relationship("LinUnconditionalFrame", secondary = "linsporadicframe_association", uselist = True)

    __mapper_args__ = {"polymorphic_identity": "LinSporadicFrame"}
    
    
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
        ForeignKey("linunconditionalframe.frame_id"),
        primary_key = True
    )

    
class LinEventTriggeredFrame(LinUnconditionalFrame):
    """
    """
    frame_id = Column(
        types.Integer, 
        ForeignKey("linunconditionalframe.frame_id"),
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
    associated_frames = relationship("LinUnconditionalFrame", secondary = "lineventtriggeredframe_association", uselist = True)
    
    __mapper_args__ = {"polymorphic_identity": "LinEventTriggeredFrame"}
   

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
        ForeignKey("linunconditionalframe.frame_id"),
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

