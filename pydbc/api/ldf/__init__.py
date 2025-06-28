#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Creational API for LDF (LIN Description File) components.

This module provides a high-level API for creating and manipulating LDF components
such as LIN networks, master/slave nodes, frames, signals, and schedule tables.
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

from typing import Optional, List, Union, Tuple

from pydbc.db import VNDB
from pydbc.db.model import (
    LinMasterNode,
    LinNetwork,
    LinNode,
    LinUnconditionalFrame,
    LinSignal,
    LinSlaveNode,
    LinEventTriggeredFrame,
    LinScheduleTable,
    LinScheduleTable_Command_Frame,
    LinSporadicFrame,
    LinSignalEncodingType,
    LinSignalEncodingEntry_Logical,
    LinSignalEncodingEntry_Physical,
    LinSignalRepresentation,
    LinUnconditionalFrameSignal,
    LinSignalSubscriber,
)


class LDFCreator:
    """High-level API for creating LDF components."""

    def __init__(self, db_path: str = ":memory:", debug: bool = False):
        """Initialize a new LDF creator.

        Args:
            db_path: Path to the database file or ":memory:" for in-memory database
            debug: Enable debug mode
        """
        self.db = VNDB.create(db_path, debug=debug)
        self.session = self.db.session
        self._networks = {}
        self._nodes = {}
        self._master_nodes = {}
        self._slave_nodes = {}
        self._frames = {}
        self._signals = {}
        self._schedule_tables = {}
        self._signal_encodings = {}

    def create_network(
        self,
        name: str,
        protocol_version: Optional[str] = None,
        language_version: Optional[str] = None,
        speed: Optional[float] = None,
        file_revision: Optional[str] = None,
        channel_name: Optional[str] = None,
        **kwargs
    ) -> LinNetwork:
        """Create a new LIN network.

        Args:
            name: Name of the network
            protocol_version: LIN protocol version
            language_version: LIN language version
            speed: Network speed in kbps
            file_revision: File revision
            channel_name: Channel name
            **kwargs: Additional network attributes

        Returns:
            The created LinNetwork object
        """
        network = LinNetwork(
            name=name,
            protocol_version=protocol_version,
            language_version=language_version,
            speed=speed,
            file_revision=file_revision,
            channel_name=channel_name,
            **kwargs
        )
        self.session.add(network)
        self._networks[name] = network
        return network

    def create_master_node(
        self,
        name: str,
        timebase: float,
        jitter: float,
        bit_length: Optional[int] = None,
        tolerant: Optional[bool] = None,
        **kwargs
    ) -> LinMasterNode:
        """Create a new LIN master node.

        Args:
            name: Name of the node
            timebase: Timebase in seconds
            jitter: Jitter in seconds
            bit_length: Bit length
            tolerant: Whether the node is tolerant
            **kwargs: Additional node attributes

        Returns:
            The created LinMasterNode object
        """
        master_node = LinMasterNode(
            name=name,
            timebase=timebase,
            jitter=jitter,
            bit_length=bit_length,
            tolerant=tolerant,
            **kwargs
        )
        self.session.add(master_node)
        self._nodes[name] = master_node
        self._master_nodes[name] = master_node
        return master_node

    def create_slave_node(
        self,
        name: str,
        protocol_version: Optional[str] = None,
        configured_NAD: Optional[int] = None,
        initial_NAD: Optional[int] = None,
        product_id: Tuple[int, int, int] = (),
        p2_min: Optional[float] = None,
        st_min: Optional[float] = None,
        n_as_timeout: Optional[float] = None,
        n_cr_timeout: Optional[float] = None,
        response_tolerance: Optional[float] = None,
        **kwargs
    ) -> LinSlaveNode:
        """Create a new LIN slave node.

        Args:
            name: Name of the node
            protocol_version: LIN protocol version
            configured_NAD: Configured NAD
            initial_NAD: Initial NAD
            product_id: Product ID tuple (supplier_id, function_id, variant)
            p2_min: P2 minimum time
            st_min: ST minimum time
            n_as_timeout: N_As timeout
            n_cr_timeout: N_Cr timeout
            response_tolerance: Response tolerance
            **kwargs: Additional node attributes

        Returns:
            The created LinSlaveNode object
        """
        slave_node = LinSlaveNode(
            name=name,
            protocol_version=protocol_version,
            configured_NAD=configured_NAD,
            initial_NAD=initial_NAD,
            product_id=product_id,
            p2_min=p2_min,
            st_min=st_min,
            n_as_timeout=n_as_timeout,
            n_cr_timeout=n_cr_timeout,
            response_tolerance=response_tolerance,
            **kwargs
        )
        self.session.add(slave_node)
        self._nodes[name] = slave_node
        self._slave_nodes[name] = slave_node
        return slave_node

    def create_signal(
        self,
        name: str,
        signal_size: int,
        init_value: Union[int, List[int]],
        publisher: Union[str, LinNode],
        **kwargs
    ) -> LinSignal:
        """Create a new LIN signal.

        Args:
            name: Name of the signal
            signal_size: Size of the signal in bits
            init_value: Initial value (integer or list of integers)
            publisher: Publisher node (name or LinNode object)
            **kwargs: Additional signal attributes

        Returns:
            The created LinSignal object
        """
        if isinstance(publisher, str):
            publisher = self._nodes[publisher]

        signal = LinSignal(
            name=name,
            signal_size=signal_size,
            init_value=init_value,
            publisher=publisher,
            **kwargs
        )
        self.session.add(signal)
        self._signals[name] = signal
        return signal

    def add_signal_subscriber(
        self, signal: Union[str, LinSignal], subscriber: Union[str, LinNode]
    ) -> LinSignalSubscriber:
        """Add a subscriber to a signal.

        Args:
            signal: Signal name or LinSignal object
            subscriber: Subscriber node name or LinNode object

        Returns:
            The created LinSignalSubscriber object
        """
        if isinstance(signal, str):
            signal = self._signals[signal]
        if isinstance(subscriber, str):
            subscriber_obj = self._nodes[subscriber]
        else:
            subscriber_obj = subscriber
        # subscriber_obj = LinSignalSubscriber(subscriber=subscriber)
        signal.subscribers.append(subscriber_obj)
        self.session.add(subscriber_obj)
        return subscriber_obj

    def create_unconditional_frame(
        self,
        name: str,
        frame_id: int,
        size: int,
        publisher: Union[str, LinNode],
        **kwargs
    ) -> LinUnconditionalFrame:
        """Create a new LIN unconditional frame.

        Args:
            name: Name of the frame
            frame_id: Frame ID
            size: Frame size in bytes
            publisher: Publisher node (name or LinNode object)
            **kwargs: Additional frame attributes

        Returns:
            The created LinUnconditionalFrame object
        """
        if isinstance(publisher, str):
            publisher = self._nodes[publisher]

        frame = LinUnconditionalFrame(
            name=name, frame_id=frame_id, size=size, publisher=publisher, **kwargs
        )
        self.session.add(frame)
        self._frames[name] = frame
        return frame

    def add_signal_to_frame(
        self,
        frame: Union[str, LinUnconditionalFrame],
        signal: Union[str, LinSignal],
        signal_offset: int = 0,
    ) -> LinUnconditionalFrameSignal:
        """Add a signal to a frame.

        Args:
            frame: Frame name or LinUnconditionalFrame object
            signal: Signal name or LinSignal object
            signal_offset: Signal offset in bits

        Returns:
            The created LinUnconditionalFrameSignal object
        """
        if isinstance(frame, str):
            frame = self._frames[frame]
        if isinstance(signal, str):
            signal = self._signals[signal]

        frame_signal = LinUnconditionalFrameSignal(
            signal=signal, signal_offset=signal_offset
        )
        frame.frame_signals.append(frame_signal)
        self.session.add(frame_signal)
        return frame_signal

    def create_event_triggered_frame(
        self,
        name: str,
        frame_id: int,
        master_node: Union[str, LinMasterNode],
        collision_resolving_schedule_table: Optional[str] = None,
        **kwargs
    ) -> LinEventTriggeredFrame:
        """Create a new LIN event-triggered frame.

        Args:
            name: Name of the frame
            frame_id: Frame ID
            master_node: Master node (name or LinMasterNode object)
            collision_resolving_schedule_table: Name of collision resolving schedule table
            **kwargs: Additional frame attributes

        Returns:
            The created LinEventTriggeredFrame object
        """
        if isinstance(master_node, str):
            master_node = self._master_nodes[master_node]

        frame = LinEventTriggeredFrame(
            name=name,
            frame_id=frame_id,
            master_node=master_node,
            collision_resolving_schedule_table=collision_resolving_schedule_table,
            **kwargs
        )
        self.session.add(frame)
        self._frames[name] = frame
        return frame

    def create_sporadic_frame(self, name: str, **kwargs) -> LinSporadicFrame:
        """Create a new LIN sporadic frame.

        Args:
            name: Name of the frame
            **kwargs: Additional frame attributes

        Returns:
            The created LinSporadicFrame object
        """
        frame = LinSporadicFrame(name=name, **kwargs)
        self.session.add(frame)
        self._frames[name] = frame
        return frame

    def create_schedule_table(self, name: str, **kwargs) -> LinScheduleTable:
        """Create a new LIN schedule table.

        Args:
            name: Name of the schedule table
            **kwargs: Additional schedule table attributes

        Returns:
            The created LinScheduleTable object
        """
        schedule_table = LinScheduleTable(name=name, **kwargs)
        self.session.add(schedule_table)
        self._schedule_tables[name] = schedule_table
        return schedule_table

    def add_frame_to_schedule_table(
        self,
        schedule_table: Union[str, LinScheduleTable],
        frame: Union[str, LinUnconditionalFrame],
        frame_time: float,
    ) -> LinScheduleTable_Command_Frame:
        """Add a frame to a schedule table.

        Args:
            schedule_table: Schedule table name or LinScheduleTable object
            frame: Frame name or LinUnconditionalFrame object
            frame_time: Frame time in seconds

        Returns:
            The created LinScheduleTable_Command_Frame object
        """
        if isinstance(schedule_table, str):
            schedule_table = self._schedule_tables[schedule_table]
        if isinstance(frame, str):
            frame = self._frames[frame]

        command = LinScheduleTable_Command_Frame(frame_time=frame_time, frame=frame)
        schedule_table.commands.append(command)
        self.session.add(command)
        return command

    def create_signal_encoding_type(self, name: str, **kwargs) -> LinSignalEncodingType:
        """Create a new LIN signal encoding type.

        Args:
            name: Name of the signal encoding type
            **kwargs: Additional signal encoding type attributes

        Returns:
            The created LinSignalEncodingType object
        """
        encoding_type = LinSignalEncodingType(name=name, **kwargs)
        self.session.add(encoding_type)
        self._signal_encodings[name] = encoding_type
        return encoding_type

    def add_logical_value_to_encoding(
        self,
        encoding_type: Union[str, LinSignalEncodingType],
        signal_value: int,
        text_info: str,
    ) -> LinSignalEncodingEntry_Logical:
        """Add a logical value to a signal encoding type.

        Args:
            encoding_type: Signal encoding type name or LinSignalEncodingType object
            signal_value: Signal value
            text_info: Text description

        Returns:
            The created LinSignalEncodingEntry_Logical object
        """
        if isinstance(encoding_type, str):
            encoding_type = self._signal_encodings[encoding_type]

        entry = LinSignalEncodingEntry_Logical(
            signal_value=signal_value, text_info=text_info
        )
        encoding_type.entries.append(entry)
        self.session.add(entry)
        return entry

    def add_physical_range_to_encoding(
        self,
        encoding_type: Union[str, LinSignalEncodingType],
        min_value: float,
        max_value: float,
        scale: float,
        offset: float,
        text_info: str,
    ) -> LinSignalEncodingEntry_Physical:
        """Add a physical range to a signal encoding type.

        Args:
            encoding_type: Signal encoding type name or LinSignalEncodingType object
            min_value: Minimum value
            max_value: Maximum value
            scale: Scale factor
            offset: Offset value
            text_info: Text description

        Returns:
            The created LinSignalEncodingEntry_Physical object
        """
        if isinstance(encoding_type, str):
            encoding_type = self._signal_encodings[encoding_type]

        entry = LinSignalEncodingEntry_Physical(
            min_value=min_value,
            max_value=max_value,
            scale=scale,
            offset=offset,
            text_info=text_info,
        )
        encoding_type.entries.append(entry)
        self.session.add(entry)
        return entry

    def add_signal_representation(
        self,
        signal: Union[str, LinSignal],
        encoding_type: Union[str, LinSignalEncodingType],
    ) -> LinSignalRepresentation:
        """Associate a signal with a signal encoding type.

        Args:
            signal: Signal name or LinSignal object
            encoding_type: Signal encoding type name or LinSignalEncodingType object

        Returns:
            The created LinSignalRepresentation object
        """
        if isinstance(signal, str):
            signal = self._signals[signal]
        if isinstance(encoding_type, str):
            encoding_type = self._signal_encodings[encoding_type]

        representation = LinSignalRepresentation(
            signal_encoding_type=encoding_type, signal=signal
        )
        self.session.add(representation)
        return representation

    def commit(self):
        """Commit changes to the database."""
        self.session.commit()

    def close(self):
        """Close the database connection."""
        self.session.close()
