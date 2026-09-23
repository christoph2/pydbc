#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Unified data model for DBC/LDF-based network databases.

The classes in this module intentionally stay independent from the SQLAlchemy ORM
and represent the common concepts used in CAN/LIN database formats.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from pathlib import Path
from typing import Any, Iterator


class BusType(Enum):
    """Supported transport busses."""

    CAN = auto()
    CANFD = auto()
    LIN = auto()
    FLEXRAY = auto()
    ETHERNET = auto()


class NodeRole(Enum):
    """High-level node roles used across bus formats."""

    MASTER = auto()
    SLAVE = auto()
    ECU = auto()
    NODE = auto()


@dataclass(slots=True)
class DataType:
    name: str
    bit_length: int
    signed: bool = False
    floating: bool = False


@dataclass(slots=True)
class Coding:
    factor: float = 1.0
    offset: float = 0.0
    minimum: float | None = None
    maximum: float | None = None
    unit: str | None = None


@dataclass(slots=True)
class Enumeration:
    values: dict[int, str] = field(default_factory=dict)


@dataclass(slots=True)
class Multiplexer:
    switch_signal: "Signal | None" = None
    cases: dict[int, list["Signal"]] = field(default_factory=dict)


@dataclass(slots=True)
class Node:
    name: str
    role: NodeRole | None = None
    attributes: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class Signal:
    name: str
    bit_length: int
    factor: float = 1.0
    offset: float = 0.0
    minimum: float | None = None
    maximum: float | None = None
    unit: str | None = None
    datatype: DataType | None = None
    sender: list[Node] = field(default_factory=list)
    receivers: list[Node] = field(default_factory=list)
    attributes: dict[str, Any] = field(default_factory=dict)
    enumeration: Enumeration | None = None


@dataclass(slots=True)
class PDU:
    name: str
    length: int
    signals: list[Signal] = field(default_factory=list)


@dataclass(slots=True)
class Bus:
    name: str
    type: BusType
    baudrate: int | None = None
    messages: list["Message"] = field(default_factory=list)
    attributes: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class Message:
    name: str
    identifier: int | None = None
    length: int = 0
    cycle_time: int | None = None
    signals: list[Signal] = field(default_factory=list)
    sender: Node | None = None
    bus: Bus | None = None
    attributes: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class NetworkDatabase:
    """Common container for all network-related objects.

    The API intentionally keeps the object model format-neutral, so both DBC and
    LDF sources can be represented with the same high-level types.
    """

    name: str = "network"
    nodes: list[Node] = field(default_factory=list)
    buses: list[Bus] = field(default_factory=list)
    messages: list[Message] = field(default_factory=list)
    signals: list[Signal] = field(default_factory=list)
    schedule_tables: list[Any] = field(default_factory=list)
    attributes: dict[str, Any] = field(default_factory=dict)

    def add_node(self, node: Node) -> Node:
        self.nodes.append(node)
        return node

    def add_bus(self, bus: Bus) -> Bus:
        self.buses.append(bus)
        return bus

    def add_message(self, message: Message) -> Message:
        self.messages.append(message)
        if message.bus is not None and message not in message.bus.messages:
            message.bus.messages.append(message)
        for signal in message.signals:
            if signal not in self.signals:
                self.signals.append(signal)
        return message

    def add_signal(self, signal: Signal, *, message: Message | None = None) -> Signal:
        if signal not in self.signals:
            self.signals.append(signal)
        if message is not None:
            if signal not in message.signals:
                message.signals.append(signal)
        return signal

    def get_message(self, name: str) -> Message | None:
        for message in self.messages:
            if message.name == name:
                return message
        return None

    def get_signal(self, name: str) -> Signal | None:
        for signal in self.signals:
            if signal.name == name:
                return signal
        return None

    def iter_messages(self) -> Iterator[Message]:
        return iter(self.messages)

    def iter_signals(self) -> Iterator[Signal]:
        return iter(self.signals)


def _coerce_session(session: Any) -> Any:
    """Accept either a SQLAlchemy session or a VNDB-like wrapper."""
    if session is None:
        return None
    return getattr(session, "session", session)


def _bus_type_for_network(network: Any) -> BusType:
    name = type(network).__name__.lower()
    if "lin" in name:
        return BusType.LIN
    if "canfd" in name:
        return BusType.CANFD
    if "flex" in name or "flexray" in name:
        return BusType.FLEXRAY
    if "ether" in name:
        return BusType.ETHERNET
    return BusType.CAN


def _node_role_for(node: Any) -> NodeRole | None:
    name = type(node).__name__.lower()
    if "linmaster" in name or "master" in name:
        return NodeRole.MASTER
    if "linslave" in name or "slave" in name:
        return NodeRole.SLAVE
    if "ecu" in name:
        return NodeRole.ECU
    return NodeRole.NODE


def _message_identifier(message: Any) -> int | None:
    for attr in ("message_id", "id", "frame_id"):
        value = getattr(message, attr, None)
        if value is not None:
            return int(value)
    return getattr(message, "rid", None)


def _signal_from_orm(signal: Any, session: Any = None) -> Signal:
    return Signal(
        name=getattr(signal, "name", str(signal)),
        bit_length=getattr(signal, "bitsize", getattr(signal, "bit_length", 0)) or 0,
        factor=getattr(signal, "formula_factor", getattr(signal, "factor", 1.0)) or 1.0,
        offset=getattr(signal, "formula_offset", getattr(signal, "offset", 0.0)) or 0.0,
        minimum=getattr(signal, "minimum", None),
        maximum=getattr(signal, "maximum", None),
        unit=getattr(signal, "unit", None),
        datatype=None,
        enumeration=_enumeration_for_signal(signal, session),
        attributes=_attributes_for_object(session, "SIGNAL", getattr(signal, "rid", None)),
    )


def _enumeration_from_dbc_signal(signal: Any) -> Enumeration | None:
    """Extract a value table (DBC ``VALUE_TABLE``/``VAL_``) as an Enumeration."""
    object_valuetable = getattr(signal, "object_valuetable", None)
    if object_valuetable is None:
        return None
    valuetable = getattr(object_valuetable, "valuetable", None)
    if valuetable is None:
        return None
    values = getattr(valuetable, "values", None) or []
    if not values:
        return None
    return Enumeration(
        values={int(vd.value): vd.value_description for vd in values}
    )


def _enumeration_from_lin_signal(signal: Any, session: Any) -> Enumeration | None:
    """Extract a LIN signal encoding type (logical values) as an Enumeration."""
    if session is None:
        return None
    signal_rid = getattr(signal, "rid", None)
    if signal_rid is None:
        return None
    try:
        from pydbc.db.model import (
            LinSignalEncodingEntry_Logical,
            LinSignalRepresentation,
        )
    except Exception:
        return None

    representation = (
        session.query(LinSignalRepresentation)
        .filter_by(signal_id=signal_rid)
        .first()
    )
    if representation is None:
        return None
    encoding_type = representation.signal_encoding_type
    if encoding_type is None:
        return None
    logical_entries = [
        entry
        for entry in (getattr(encoding_type, "entries", None) or [])
        if isinstance(entry, LinSignalEncodingEntry_Logical)
    ]
    if not logical_entries:
        return None
    return Enumeration(
        values={int(entry.signal_value): entry.text_info for entry in logical_entries}
    )


def _enumeration_for_signal(signal: Any, session: Any) -> Enumeration | None:
    enumeration = _enumeration_from_dbc_signal(signal)
    if enumeration is not None:
        return enumeration
    return _enumeration_from_lin_signal(signal, session)


# DBC ``Attribute_Definition.objecttype`` values (see ``pydbc.types.AttributeType``).
_ATTRIBUTE_OBJECT_TYPES = {
    "NODE": 0,
    "MESSAGE": 1,
    "SIGNAL": 2,
    "ENV_VAR": 3,
    "NETWORK": 4,
}

# DBC ``Attribute_Definition.valuetype`` values (see ``pydbc.types.ValueType``).
_NUMERIC_ATTRIBUTE_VALUE_TYPES = {0, 1, 2}  # INT, HEX, FLOAT
_INTEGRAL_ATTRIBUTE_VALUE_TYPES = {0, 1}  # INT, HEX


def _attributes_for_object(
    session: Any, object_kind: str, rid: int | None
) -> dict[str, Any]:
    """Fetch DBC ``Attribute_Value`` entries for a given object as a plain dict.

    ``object_kind`` is one of ``"NODE"``, ``"MESSAGE"``, ``"SIGNAL"`` or
    ``"NETWORK"`` and is mapped to the corresponding ``Attribute_Definition``
    object type. Returns an empty dict for LIN sources or when no attributes
    are present.
    """
    if session is None or rid is None:
        return {}
    object_type = _ATTRIBUTE_OBJECT_TYPES.get(object_kind)
    if object_type is None:
        return {}
    try:
        from pydbc.db.model import Attribute_Definition, Attribute_Value
    except Exception:
        return {}

    rows = (
        session.query(Attribute_Value)
        .join(
            Attribute_Definition,
            Attribute_Value.attribute_definition_id == Attribute_Definition.rid,
        )
        .filter(
            Attribute_Definition.objecttype == object_type,
            Attribute_Value.object_id == rid,
        )
        .all()
    )
    result: dict[str, Any] = {}
    for row in rows:
        definition = row.attribute_definition
        if definition is None:
            continue
        if definition.valuetype in _NUMERIC_ATTRIBUTE_VALUE_TYPES:
            if row.num_value is None:
                value: Any = None
            elif definition.valuetype in _INTEGRAL_ATTRIBUTE_VALUE_TYPES:
                value = int(row.num_value)
            else:
                value = row.num_value
        else:
            value = row.string_value
        result[definition.name] = value
    return result


def _node_from_orm(node: Any, session: Any = None) -> Node:
    rid = getattr(node, "rid", None)
    attributes: dict[str, Any] = {
        "rid": rid,
        "node_id": getattr(node, "node_id", None),
    }
    attributes.update(_attributes_for_object(session, "NODE", rid))
    return Node(
        name=getattr(node, "name", str(node)),
        role=_node_role_for(node),
        attributes=attributes,
    )


def as_network_database(session: Any, *, name: str = "network") -> NetworkDatabase:
    """Create a uniform database view from an existing ORM session.

    The adapter accepts either a SQLAlchemy session object or a container exposing
    a ``session`` attribute (for example a VNDB instance produced by the importers).
    """
    session = _coerce_session(session)
    database = NetworkDatabase(name=name)
    if session is None:
        return database

    try:
        from pydbc.db.model import Message as DbMessage
        from pydbc.db.model import Network as DbNetwork
        from pydbc.db.model import Node as DbNode
        from pydbc.db.model import Signal as DbSignal
    except Exception:
        return database

    node_by_rid: dict[int, Node] = {}
    for node in session.query(DbNode).all():
        node_obj = _node_from_orm(node, session)
        node_by_rid[getattr(node, "rid", None)] = node_obj
        database.add_node(node_obj)

    for network in session.query(DbNetwork).all():
        database.add_bus(
            Bus(
                name=getattr(network, "name", str(network)),
                type=_bus_type_for_network(network),
                baudrate=getattr(network, "baudrate", None),
                messages=[],
                attributes=_attributes_for_object(
                    session, "NETWORK", getattr(network, "rid", None)
                ),
            )
        )

    message_by_rid: dict[int, Message] = {}
    for message in session.query(DbMessage).all():
        message_obj = Message(
            name=getattr(message, "name", str(message)),
            identifier=_message_identifier(message),
            length=getattr(message, "dlc", 0) or 0,
            cycle_time=getattr(message, "cycle_time", None),
            sender=None,
            bus=None,
            attributes=_attributes_for_object(
                session, "MESSAGE", getattr(message, "rid", None)
            ),
        )
        if getattr(message, "sender", None) is not None:
            sender_id = message.sender
            for rid, node in node_by_rid.items():
                if rid == sender_id:
                    message_obj.sender = node
                    break
        for signal in list(getattr(message, "signals", []) or []):
            signal_obj = _signal_from_orm(signal, session)
            if signal_obj not in database.signals:
                database.add_signal(signal_obj)
            if signal_obj not in message_obj.signals:
                message_obj.signals.append(signal_obj)
        database.add_message(message_obj)
        if getattr(message, "rid", None) is not None:
            message_by_rid[int(message.rid)] = message_obj

    for signal in session.query(DbSignal).all():
        signal_obj = _signal_from_orm(signal, session)
        if signal_obj.name not in {item.name for item in database.signals}:
            database.add_signal(signal_obj)

    for message in session.query(DbMessage).all():
        for relation in list(getattr(message, "message_signals", []) or []):
            signal = relation.signal if relation is not None else None
            if signal is None:
                continue
            signal_obj = next((item for item in database.signals if item.name == signal.name), None)
            if signal_obj is None:
                signal_obj = _signal_from_orm(signal, session)
                database.add_signal(signal_obj)
            if signal_obj not in database.get_message(message.name).signals:
                database.get_message(message.name).signals.append(signal_obj)

    return database


def load_database(file_path: str | Path, *, format: str | None = None) -> NetworkDatabase:
    """Load a DBC or LDF file and return the common abstract model."""
    path = Path(file_path)
    source_format = (format or path.suffix.lower().lstrip(".") or "").upper()

    if source_format in {"DBC", "DB"}:
        from pydbc.api import import_dbc

        session = import_dbc(path, as_vndb=False)
        return as_network_database(session, name=path.stem)
    if source_format in {"LDF", "LIN"}:
        from pydbc.api import import_ldf

        session = import_ldf(path, as_vndb=False)
        return as_network_database(session, name=path.stem)
    raise ValueError(f"Unsupported database format: {source_format or path.suffix!r}")


__all__ = [
    "BusType",
    "NodeRole",
    "DataType",
    "Coding",
    "Enumeration",
    "Multiplexer",
    "Node",
    "Signal",
    "PDU",
    "Bus",
    "Message",
    "NetworkDatabase",
    "as_network_database",
    "load_database",
]
