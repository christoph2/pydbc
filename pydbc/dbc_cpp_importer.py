#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Import DBC files using the C++ DBC parser.

This module converts the parsed DBC AST into VNDB (SQLAlchemy) records.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Optional

from sqlalchemy import func
from pydbc.db import VNDB
from pydbc.db.model import (
    Attribute_Definition,
    Attribute_Value,
    AttributeRel_Value,
    Dbc_Version,
    EnvVar,
    Message,
    Message_Signal,
    Network,
    Node,
    Node_TxMessage,
    Node_RxSignal,
    Object_Valuetable,
    Signal,
    Signal_Group,
    Signal_Group_Signal,
    Value_Description,
    Valuetable,
    Vndb_Protocol,
    VndbMeta,
)
from pydbc.types import AttributeType, BusType, ValueType

try:
    from pydbc.cpp_ext.dbc_extension import DbcParser, AttributeDefinition, AttributeValue, Comment  # type: ignore
except Exception:
    DbcParser = None  # type: ignore


def _ensure_parser():
    if DbcParser is None:
        raise RuntimeError(
            "C++ DBC parser extension is not available. Build the extension with build_ext.py"
        )
    return DbcParser


def import_dbc_cpp(
    file_path: str | Path,
    *,
    encoding: Optional[str] = None,
    debug: bool = False,
    logLevel: str = "WARN",
    in_memory: bool = False,
) -> object:
    """Import a .dbc file using the C++ DBC parser."""
    path = Path(file_path)
    if not path.exists() or not path.is_file():
        raise FileNotFoundError(f"Input file not found: {path}")

    from pydbc.utils import detect_encoding

    enc = encoding or detect_encoding(str(path))

    # Read the file and ensure we have it as UTF-8 for the C++ parser
    # if it's not already. Actually, we read it with the detected encoding
    # and pass it to C++ which we just updated to handle Latin-1 -> UTF-8
    # for strings, but if we pass it as a Python string, pybind11 will
    # convert it to UTF-8 std::string.
    try:
        content = path.read_text(encoding=enc)
    except UnicodeDecodeError:
        # Fallback to latin1 if detection failed
        content = path.read_text(encoding="latin1")

    parser = _ensure_parser()(str(path), content)
    ast = parser.parse()
    if parser.get_diagnostics():
        # Filter for errors
        errors = [d for d in parser.get_diagnostics() if d.severity == d.Severity.Error]
        if errors:
            messages = "; ".join(d.message for d in errors)
            raise RuntimeError(f"DBC parsing failed: {messages}")
    db_file_name = path.with_suffix(".vndb").as_posix() if not in_memory else ":memory:"
    vndb = VNDB.create(
        db_file_name, debug=debug, logLevel=logLevel
    )
    session = vndb.session

    # 1. Network & Protocol
    network = Network(name=vndb.dbname)
    session.add(network)
    proto = Vndb_Protocol(network=network, name=BusType.CAN.name, specific=None)
    session.add(proto)
    session.flush()

    # 2. Version
    if ast.version:
        session.add(Dbc_Version(version_string=ast.version, network=network.rid))

    # 3. Nodes
    nodes: dict[str, Node] = {}
    # Always include Vector__XXX
    for node_name in list(ast.nodes) + ["Vector__XXX"]:
        if node_name not in nodes:
            # Check for existing node with same name in database (case-insensitive in SQLite for some configurations)
            # or just rely on the fact that we might have already added it if it was in ast.nodes.
            # However, DbcParser.nodes usually contains unique names from the DBC.
            node = Node(name=node_name)
            session.add(node)
            nodes[node_name] = node
    try:
        session.flush()
    except Exception:
        session.rollback()
        # Fallback: add nodes one by one and skip duplicates
        nodes.clear()
        for node_name in list(ast.nodes) + ["Vector__XXX"]:
            if node_name not in nodes:
                # Check if it already exists in DB
                existing = session.query(Node).filter(Node.name == node_name).first()
                if not existing:
                    # Try case-insensitive check if still failing
                    existing = (
                        session.query(Node)
                        .filter(func.lower(Node.name) == node_name.lower())
                        .first()
                    )

                if existing:
                    nodes[node_name] = existing
                else:
                    node = Node(name=node_name)
                    session.add(node)
                    try:
                        session.flush()
                        nodes[node_name] = node
                    except Exception:
                        session.rollback()
                        # Last resort: find whatever is there
                        existing = (
                            session.query(Node)
                            .filter(func.lower(Node.name) == node_name.lower())
                            .first()
                        )
                        if existing:
                            nodes[node_name] = existing
    session.flush()

    # 4. Value Tables
    value_tables: dict[str, Valuetable] = {}
    for vt_def in ast.value_tables:
        vt = Valuetable(name=vt_def.name)
        session.add(vt)
        session.flush()
        value_tables[vt_def.name] = vt
        for desc_def in vt_def.descriptions:
            vd = Value_Description(
                valuetable_id=vt.rid,
                value=desc_def.value,
                value_description=desc_def.description,
            )
            session.add(vd)
    session.flush()

    # Create mapping for object value tables (VAL_ section)
    # The C++ parser puts VAL_ entries into ast.value_tables but uses a specific name format for signals: "msgId signalName"
    signal_vt_map = {}
    for vt_name, vt in value_tables.items():
        if " " in vt_name:
            try:
                msg_id_str, sig_name = vt_name.split(" ", 1)
                msg_id = int(msg_id_str)
                signal_vt_map[(msg_id, sig_name)] = vt
            except ValueError:
                pass

    # 5. Messages & Signals
    messages: dict[int, Message] = {}
    db_signals: dict[tuple[int, str], Signal] = {}  # (msg_id, sig_name) -> Signal

    for msg_def in ast.messages:
        tx_node = nodes.get(msg_def.transmitter)
        if not tx_node:
            tx_node = nodes["Vector__XXX"]

        msg = Message(
            name=msg_def.name,
            message_id=msg_def.id,
            dlc=msg_def.size,
            sender=tx_node.rid,
        )
        session.add(msg)
        session.flush()
        messages[msg_def.id] = msg

        for sig_def in msg_def.signals:
            sign = 1 if sig_def.sign == "+" else -1
            byte_order = (
                1 if sig_def.byte_order == "1" or sig_def.byte_order == 1 else 0
            )

            sig = Signal(
                name=sig_def.name,
                bitsize=sig_def.size,
                byteorder=byte_order,
                sign=sign,
                formula_factor=sig_def.factor,
                formula_offset=sig_def.offset,
                minimum=sig_def.minimum,
                maximum=sig_def.maximum,
                unit=sig_def.unit,
            )
            session.add(sig)
            session.flush()
            db_signals[(msg_def.id, sig_def.name)] = sig

            # Link Signal to Valuetable if present
            vt = signal_vt_map.get((msg_def.id, sig_def.name))
            if vt:
                ovt = Object_Valuetable(
                    object_type=0,  # Signal
                    object_rid=sig.rid,
                    valuetable_id=vt.rid,
                )
                session.add(ovt)

            # Multiplexer logic
            m_indicator = sig_def.multiplexer_indicator
            m_signal = None
            m_dependent = None
            m_value = None
            if m_indicator:
                if m_indicator == "M":
                    m_signal = 1
                    m_dependent = 0
                elif m_indicator.startswith("m"):
                    m_signal = 0
                    m_dependent = 1
                    try:
                        m_value = int(m_indicator[1:])
                    except ValueError:
                        pass

            ms = Message_Signal(
                offset=sig_def.start_bit,
                multiplexor_signal=m_signal,
                multiplex_dependent=m_dependent,
                multiplexor_value=m_value,
                signal=sig,
                message=msg,
            )
            session.add(ms)

            # Receivers
            for rcv_name in sig_def.receivers:
                rcv_node = nodes.get(rcv_name)
                if rcv_node:
                    rxs = Node_RxSignal(
                        node_id=rcv_node.rid, message_id=msg.rid, signal_id=sig.rid
                    )
                    session.add(rxs)
    session.flush()

    # 6. Environment Variables
    env_vars: dict[str, EnvVar] = {}
    for ev_def in ast.environment_variables:
        ev = EnvVar(
            name=ev_def.name,
            type=ev_def.type,
            unit=ev_def.unit,
            minimum=ev_def.min,
            maximum=ev_def.max,
            access=ev_def.id,  # In DbcListener it uses accessType extracted from DUMMY_NODE_VECTOR, but here it seems ev_def.id is used?
            startup_value=ev_def.initial_value,
            size=0,  # Default
        )
        session.add(ev)
        for node_name in ev_def.access_nodes:
            node = nodes.get(node_name)
            if node:
                ev.accessingNodes.append(node)
        env_vars[ev_def.name] = ev
    session.flush()

    # 7. Attribute Definitions
    attr_defs: dict[str, Attribute_Definition] = {}
    for ad_def in ast.attribute_definitions:
        if ad_def.name in attr_defs:
            continue

        # Check if it already exists in DB (e.g. from a previous partial import or shared DB)
        existing_ad = (
            session.query(Attribute_Definition)
            .filter(Attribute_Definition.name == ad_def.name)
            .first()
        )
        if existing_ad:
            attr_defs[ad_def.name] = existing_ad
            continue
        obj_type = AttributeType.NETWORK
        if ad_def.object_type == ad_def.ObjectType.Node:
            obj_type = AttributeType.NODE
        elif ad_def.object_type == ad_def.ObjectType.Message:
            obj_type = AttributeType.MESSAGE
        elif ad_def.object_type == ad_def.ObjectType.Signal:
            obj_type = AttributeType.SIGNAL
        elif ad_def.object_type == ad_def.ObjectType.EnvVar:
            obj_type = AttributeType.ENV_VAR
        elif ad_def.object_type == ad_def.ObjectType.NodeBoRel:
            obj_type = AttributeType.REL_NODE
        elif ad_def.object_type == ad_def.ObjectType.NodeSignalRel:
            obj_type = AttributeType.REL_SIGNAL
        elif ad_def.object_type == ad_def.ObjectType.NodeEvRel:
            obj_type = AttributeType.REL_ENV_VAR

        # Map ValueType
        val_type = ValueType.STRING
        if ad_def.value_type == "INT":
            val_type = ValueType.INT
        elif ad_def.value_type == "HEX":
            val_type = ValueType.HEX
        elif ad_def.value_type == "FLOAT":
            val_type = ValueType.FLOAT
        elif ad_def.value_type == "ENUM":
            val_type = ValueType.ENUM

        ad = Attribute_Definition(
            name=ad_def.name,
            objecttype=obj_type,
            valuetype=val_type,
            minimum=ad_def.min,
            maximum=ad_def.max,
            enumvalues=";".join(ad_def.enum_values) if ad_def.enum_values else None,
        )
        session.add(ad)
        attr_defs[ad_def.name] = ad
    session.flush()

    # 8. Attribute Defaults (Simplified: now directly in AttributeDefinition)
    for ad_def in ast.attribute_definitions:
        if hasattr(ad_def, "default_value") and ad_def.default_value is not None:
            ad = attr_defs.get(ad_def.name)
            if ad:
                if ad.valuetype in (ValueType.INT, ValueType.HEX, ValueType.FLOAT):
                    try:
                        ad.default_number = float(ad_def.default_value)
                    except ValueError:
                        pass
                else:
                    ad.default_string = str(ad_def.default_value)
    session.flush()

    # 9. Attribute Values
    # Use a dict to track (object_id, attribute_definition_id) to avoid IntegrityError
    # when multiple BA_ entries exist for the same object in DBC.
    attr_values_map = {}
    attr_rel_values_map = {}

    for av_def in ast.attribute_values:
        ad = attr_defs.get(av_def.name)
        if not ad:
            continue

        rid = 0
        opt_id1 = None
        opt_id2 = None

        if av_def.object_type == av_def.ObjectType.Node:
            node = nodes.get(av_def.object_name)
            rid = node.rid if node else 0
        elif av_def.object_type == av_def.ObjectType.Message:
            msg = messages.get(av_def.message_id)
            rid = msg.rid if msg else 0
        elif av_def.object_type == av_def.ObjectType.Signal:
            sig = db_signals.get((av_def.message_id, av_def.object_name))
            rid = sig.rid if sig else 0
        elif av_def.object_type == av_def.ObjectType.EnvVar:
            ev = env_vars.get(av_def.object_name)
            rid = ev.rid if ev else 0
        elif av_def.object_type in (
            av_def.ObjectType.NodeBoRel,
            av_def.ObjectType.NodeSignalRel,
            av_def.ObjectType.NodeEvRel,
        ):
            # Relative attributes
            node = nodes.get(av_def.object_name)
            opt_id1 = node.rid if node else None

            if av_def.object_type == av_def.ObjectType.NodeBoRel:
                msg = messages.get(av_def.message_id)
                rid = msg.rid if msg else 0
                opt_id2 = av_def.message_id
            elif av_def.object_type == av_def.ObjectType.NodeSignalRel:
                sig = db_signals.get((av_def.message_id, av_def.second_object_name))
                rid = sig.rid if sig else 0
                opt_id2 = av_def.message_id
            elif av_def.object_type == av_def.ObjectType.NodeEvRel:
                ev = env_vars.get(av_def.second_object_name)
                rid = ev.rid if ev else 0

            num_val = None
            str_val = None
            try:
                num_val = float(av_def.value)
            except ValueError:
                str_val = av_def.value

            rel_key = (rid, ad.rid, opt_id1, opt_id2)
            if rel_key in attr_rel_values_map:
                arv = attr_rel_values_map[rel_key]
                arv.num_value = num_val
                arv.string_value = str_val
            else:
                # Check if it already exists in DB
                existing_arv = (
                    session.query(AttributeRel_Value)
                    .filter(
                        AttributeRel_Value.object_id == rid,
                        AttributeRel_Value.attribute_definition_id == ad.rid,
                        AttributeRel_Value.opt_object_id_1 == opt_id1,
                        AttributeRel_Value.opt_object_id_2 == opt_id2,
                    )
                    .first()
                )
                if existing_arv:
                    existing_arv.num_value = num_val
                    existing_arv.string_value = str_val
                    attr_rel_values_map[rel_key] = existing_arv
                else:
                    arv = AttributeRel_Value(
                        object_id=rid,
                        attribute_definition=ad,
                        num_value=num_val,
                        string_value=str_val,
                        opt_object_id_1=opt_id1,
                        opt_object_id_2=opt_id2,
                    )
                    session.add(arv)
                    attr_rel_values_map[rel_key] = arv
            continue  # Already handled relative value

        num_val = None
        str_val = None
        if ad.valuetype in (ValueType.INT, ValueType.HEX, ValueType.FLOAT):
            try:
                num_val = float(av_def.value)
            except ValueError:
                pass
        else:
            str_val = av_def.value

        key = (rid, ad.rid)
        if key in attr_values_map:
            av = attr_values_map[key]
            av.num_value = num_val
            av.string_value = str_val
        else:
            # Check if it already exists in DB
            existing_av = (
                session.query(Attribute_Value)
                .filter(
                    Attribute_Value.object_id == rid,
                    Attribute_Value.attribute_definition_id == ad.rid,
                )
                .first()
            )
            if existing_av:
                existing_av.num_value = num_val
                existing_av.string_value = str_val
                attr_values_map[key] = existing_av
            else:
                av = Attribute_Value(
                    object_id=rid,
                    attribute_definition=ad,
                    num_value=num_val,
                    string_value=str_val,
                )
                session.add(av)
                attr_values_map[key] = av
    session.flush()

    # 10. Comments
    for comm in ast.comments:
        target = None
        if comm.type == comm.Type.Node:
            target = nodes.get(comm.name)
        elif comm.type == comm.Type.Message:
            target = messages.get(comm.id)
        elif comm.type == comm.Type.Signal:
            target = db_signals.get((comm.id, comm.name))
        elif comm.type == comm.Type.EnvVar:
            target = env_vars.get(comm.name)
        elif comm.type == comm.Type.Generic:
            target = network

        if target:
            target.comment = comm.comment
    session.flush()

    # 11. Message Transmitters
    for mt_def in ast.message_transmitters:
        msg = messages.get(mt_def.message_id)
        if not msg:
            continue
        for node_name in mt_def.transmitters:
            node = nodes.get(node_name)
            if node:
                session.add(Node_TxMessage(node=node, message=msg))
    session.flush()

    # 12. Signal Groups
    for sg_def in ast.signal_groups:
        msg = messages.get(sg_def.message_id)
        if not msg:
            continue
        sg = Signal_Group(name=sg_def.name, value=sg_def.value, message=msg)
        session.add(sg)
        session.flush()
        for sig_name in sg_def.signals:
            sig = db_signals.get((sg_def.message_id, sig_name))
            if sig:
                session.add(
                    Signal_Group_Signal(signal_group=sg, message=msg, signal=sig)
                )
    session.flush()

    # 13. Signal Extended Value Types
    for sevt_def in ast.signal_extended_value_types:
        sig = db_signals.get((sevt_def.message_id, sevt_def.signal_name))
        if sig:
            sig.valuetype = sevt_def.value_type
    session.flush()

    # Finalize
    meta_entry = VndbMeta(schema_version=1, vndb_type=1)
    session.add(meta_entry)
    session.commit()
    return session


__all__ = ["import_dbc_cpp"]
