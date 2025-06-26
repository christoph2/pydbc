#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Creational API for DBC (CAN Database) components.

This module provides a high-level API for creating and manipulating DBC components
such as networks, nodes, messages, and signals.
"""

__copyright__ = """
   pySART - Simplified AUTOSAR-Toolkit for Python.

   (C) 2010-2023 by Christoph Schueler <cpu12.gems.googlemail.com>

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

from typing import Optional, Union, Dict, Any

from pydbc.db import VNDB
from pydbc.db.model import (
    Network,
    Node,
    Message,
    Signal,
    Message_Signal,
    Value_Description,
    Valuetable,
    Node_RxSignal,
    Attribute_Definition,
    Attribute_Value,
)


class DBCCreator:
    """High-level API for creating DBC components."""

    def __init__(self, db_path: str = ":memory:", debug: bool = False):
        """Initialize a new DBC creator.

        Args:
            db_path: Path to the database file or ":memory:" for in-memory database
            debug: Enable debug mode
        """
        self.db = VNDB.create(db_path, debug=debug)
        self.session = self.db.session
        self._networks = {}
        self._nodes = {}
        self._messages = {}
        self._signals = {}
        self._valuetables = {}

    def create_network(self, name: str, **kwargs) -> Network:
        """Create a new network.

        Args:
            name: Name of the network
            **kwargs: Additional network attributes

        Returns:
            The created Network object
        """
        network = Network(name=name, **kwargs)
        self.session.add(network)
        self._networks[name] = network
        return network

    def create_node(self, name: str, **kwargs) -> Node:
        """Create a new node.

        Args:
            name: Name of the node
            **kwargs: Additional node attributes

        Returns:
            The created Node object
        """
        node = Node(name=name, **kwargs)
        self.session.add(node)
        self._nodes[name] = node
        return node

    def create_message(
        self,
        name: str,
        message_id: int,
        dlc: int,
        sender: Union[str, Node, int],
        **kwargs
    ) -> Message:
        """Create a new message.

        Args:
            name: Name of the message
            message_id: Message ID
            dlc: Data Length Code (message size in bytes)
            sender: Sender node (name, Node object, or rid)
            **kwargs: Additional message attributes

        Returns:
            The created Message object
        """
        if isinstance(sender, str):
            sender_rid = self._nodes[sender].rid
        elif isinstance(sender, Node):
            sender_rid = sender.rid
            
        message = Message(name=name, message_id=message_id, dlc=dlc, sender=sender_rid, **kwargs)
        self.session.add(message)
        self._messages[name] = message
        return message

    def create_signal(
        self,
        name: str,
        bitsize: int,
        byteorder: int = 1,
        sign: int = 1,
        formula_factor: float = 1.0,
        formula_offset: float = 0.0,
        minimum: float = 0.0,
        maximum: float = 0.0,
        unit: str = "",
        **kwargs
    ) -> Signal:
        """Create a new signal.

        Args:
            name: Name of the signal
            bitsize: Size of the signal in bits
            byteorder: Byte order (1 for little endian, 0 for big endian)
            sign: Sign (1 for unsigned, 0 for signed)
            formula_factor: Factor for physical value calculation
            formula_offset: Offset for physical value calculation
            minimum: Minimum value
            maximum: Maximum value
            unit: Unit of the signal
            **kwargs: Additional signal attributes

        Returns:
            The created Signal object
        """
        signal = Signal(
            name=name,
            bitsize=bitsize,
            byteorder=byteorder,
            sign=sign,
            formula_factor=formula_factor,
            formula_offset=formula_offset,
            minimum=minimum,
            maximum=maximum,
            unit=unit,
            **kwargs
        )
        self.session.add(signal)
        self._signals[name] = signal
        return signal

    def add_signal_to_message(
        self,
        message: Union[str, Message],
        signal: Union[str, Signal],
        offset: int,
        multiplexor_signal: Optional[int] = None,
        multiplex_dependent: Optional[bool] = None,
        multiplexor_value: Optional[int] = None,
    ) -> Message_Signal:
        """Add a signal to a message.

        Args:
            message: Message name or Message object
            signal: Signal name or Signal object
            offset: Bit offset in the message
            multiplexor_signal: Multiplexor signal ID
            multiplex_dependent: Whether the signal is multiplex dependent
            multiplexor_value: Multiplexor value

        Returns:
            The created Message_Signal object
        """
        if isinstance(message, str):
            message = self._messages[message]
        if isinstance(signal, str):
            signal = self._signals[signal]

        msg_sig = Message_Signal(
            message=message,
            signal=signal,
            offset=offset,
            multiplexor_signal=multiplexor_signal,
            multiplex_dependent=multiplex_dependent,
            multiplexor_value=multiplexor_value,
        )
        self.session.add(msg_sig)
        return msg_sig

    def create_valuetable(self, name: str, values: Dict[int, str]) -> Valuetable:
        """Create a value table for signal value descriptions.

        Args:
            name: Name of the value table
            values: Dictionary mapping values to descriptions

        Returns:
            The created Valuetable object
        """
        value_descriptions = []
        for value, description in values.items():
            vd = Value_Description(value=value, value_description=description)
            value_descriptions.append(vd)
            self.session.add(vd)

        valuetable = Valuetable(name=name, values=value_descriptions)
        self.session.add(valuetable)
        self._valuetables[name] = valuetable
        return valuetable

    def add_node_as_receiver(
        self, signal: Union[str, Signal], node: Union[str, Node]
    ) -> Node_RxSignal:
        """Add a node as a receiver for a signal.

        Args:
            signal: Signal name or Signal object
            node: Node name or Node object

        Returns:
            The created Node_RxSignal object
        """
        if isinstance(signal, str):
            signal = self._signals[signal]
        if isinstance(node, str):
            node = self._nodes[node]

        node_rx_signal = Node_RxSignal(signal=signal, node=node)
        self.session.add(node_rx_signal)
        return node_rx_signal

    def create_attribute_definition(
        self, name: str, object_type: str, value_type: str, **kwargs
    ) -> Attribute_Definition:
        """Create an attribute definition.

        Args:
            name: Name of the attribute
            object_type: Type of object the attribute applies to
            value_type: Type of the attribute value
            **kwargs: Additional attribute definition properties

        Returns:
            The created Attribute_Definition object
        """
        attr_def = Attribute_Definition(
            name=name, object_type=object_type, value_type=value_type, **kwargs
        )
        self.session.add(attr_def)
        return attr_def

    def set_attribute_value(
        self,
        attribute_definition: Union[str, Attribute_Definition],
        object_id: int,
        value: Any,
    ) -> Attribute_Value:
        """Set an attribute value for an object.

        Args:
            attribute_definition: Attribute definition name or object
            object_id: ID of the object to set the attribute for
            value: Value to set

        Returns:
            The created Attribute_Value object
        """
        if isinstance(attribute_definition, str):
            attribute_definition = (
                self.session.query(Attribute_Definition)
                .filter_by(name=attribute_definition)
                .first()
            )

        attr_value = Attribute_Value(
            attribute_definition=attribute_definition,
            object_id=object_id,
            value=str(value),
        )
        self.session.add(attr_value)
        return attr_value

    def commit(self):
        """Commit changes to the database."""
        self.session.commit()

    def close(self):
        """Close the database connection."""
        self.session.close()
