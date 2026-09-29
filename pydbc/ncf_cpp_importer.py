#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Import Node Capability Files using the C++ NCF parser.

This module converts the parsed NCF AST into VNDB (SQLAlchemy) records,
mirroring the behavior of ``NcfListener`` but driven by the C++ parser.
"""

from __future__ import annotations
from typing import Optional
from pathlib import Path

from pydbc.db import VNDB
from pydbc.db.model import (
    LinNetwork,
    LinSlaveNode,
    LinSignal,
    LinSignalEncodingType,
    LinSignalEncodingEntry_Logical,
    LinSignalEncodingEntry_Physical,
    LinSignalEncodingEntry_Value,
    LinSignalRepresentation,
    LinUnconditionalFrame,
    LinResponseErrorSignal,
    LinFaultStateSignal,
    Vndb_Protocol,
)
from pydbc.types import BusType

try:
    from pydbc.cpp_ext.ncf_extension import NcfParser  # type: ignore
except Exception:
    NcfParser = None  # type: ignore


def _ensure_parser():
    if NcfParser is None:
        raise RuntimeError(
            "C++ NCF parser extension is not available. Build the extension with build_ext.py"
        )
    return NcfParser


def import_ncf_cpp(
    file_path: str | Path,
    *,
    encoding: Optional[str] = None,
    debug: bool = False,
    logLevel: str = "WARN",
) -> object:
    """Import a .ncf file using the C++ NCF parser."""
    path = Path(file_path)
    if not path.exists() or not path.is_file():
        raise FileNotFoundError(f"Input file not found: {path}")

    from pydbc.utils import detect_encoding

    enc = encoding or detect_encoding(str(path))
    try:
        content = path.read_text(encoding=enc)
    except UnicodeDecodeError:
        content = path.read_text(encoding="latin1")

    parser = _ensure_parser()(str(path), content)
    ast = parser.parse()
    if parser.get_diagnostics():
        messages = "; ".join(d.message for d in parser.get_diagnostics())
        raise RuntimeError(f"NCF parsing failed: {messages}")

    vndb = VNDB.create(
        path.with_suffix(".vndb").as_posix(), debug=debug, logLevel=logLevel
    )
    session = vndb.session

    network = LinNetwork(
        name=vndb.dbname,
        language_version=ast.language_version,
    )
    session.add(network)
    session.add(Vndb_Protocol(network=network, name=BusType.LIN.name, specific=None))
    session.flush()

    for node_def in ast.nodes:
        _insert_node(session, node_def)

    session.commit()
    return session


def _insert_node(session, node_def) -> None:
    gen = node_def.general
    diag = node_def.diagnostic

    node = LinSlaveNode(
        name=node_def.name,
        protocol_version=gen.protocol_version,
        configured_NAD=diag.nad_lhs,
        initial_NAD=diag.nad_rhs,
        product_id=(gen.supplier_id, gen.function_id, gen.variant_id),
        p2_min=diag.p2_min,
        st_min=diag.st_min,
        n_as_timeout=diag.n_as_timeout,
        n_cr_timeout=diag.n_cr_timeout,
    )
    session.add(node)
    session.flush()

    # Map signal name -> LinSignal for this node (used later for status mgmt)
    signal_map: dict[str, object] = {}

    for frame in node_def.frames:
        _insert_frame(session, frame, node, signal_map)

    # Encoding types
    enc_map: dict[str, object] = {}
    for enc in node_def.encodings:
        lse = _insert_encoding(session, enc)
        enc_map[enc.name] = lse

    # Signal representations (encoding_name referenced in signal properties)
    for frame in node_def.frames:
        for sig_def in frame.signals:
            enc_name = sig_def.properties.encoding_name
            if enc_name and enc_name in enc_map and sig_def.name in signal_map:
                signal = signal_map[sig_def.name]
                lse = enc_map[enc_name]
                session.add(
                    LinSignalRepresentation(signal_encoding_type=lse, signal=signal)
                )

    # Status management
    status = node_def.status
    if status.response_error and status.response_error in signal_map:
        signal = signal_map[status.response_error]
        session.add(LinResponseErrorSignal(node=node, signal=signal))

    for fs_name in status.fault_state_signals:
        if fs_name in signal_map:
            signal = signal_map[fs_name]
            session.add(LinFaultStateSignal(node=node, signal=signal))

    session.flush()


def _insert_frame(session, frame, node, signal_map: dict) -> None:
    # 'publish' frames: the node is the publisher; 'subscribe': node is subscriber
    # For simplicity create a LinUnconditionalFrame with this node as publisher for
    # published frames, and store subscribe frames as publisher too (no separate
    # subscriber relationship in the simple NCF model).
    props = frame.properties
    msg = LinUnconditionalFrame(
        name=frame.name,
        frame_id=0,  # NCF does not specify frame IDs
        size=props.length,
        publisher=node,
    )
    session.add(msg)
    session.flush()

    for sig_def in frame.signals:
        p = sig_def.properties
        if p.init_value.is_array:
            init_val = p.init_value.array_values
        else:
            init_val = p.init_value.scalar
        signal = LinSignal(
            name=sig_def.name,
            signal_size=p.size,
            init_value=init_val,
            publisher=node,
        )
        session.add(signal)
        session.flush()
        msg.add_signal(signal, p.offset)
        signal_map[sig_def.name] = signal

    session.flush()


def _insert_encoding(session, enc) -> LinSignalEncodingType:
    lse = LinSignalEncodingType(name=enc.name)
    session.add(lse)
    for value in enc.values:
        if value.type == "logical" and value.logical_value:
            lv = value.logical_value
            text = lv.text_info if lv.text_info else None
            entry = LinSignalEncodingEntry_Logical(
                signal_value=lv.signal_value,
                text_info=text,
            )
        elif value.type == "physical" and value.physical_range:
            pr = value.physical_range
            text = pr.text_info if pr.text_info else None
            entry = LinSignalEncodingEntry_Physical(
                min_value=pr.min_value,
                max_value=pr.max_value,
                scale=pr.scale,
                offset=pr.offset_val,
                text_info=text,
            )
        elif value.type == "bcd":
            entry = LinSignalEncodingEntry_Value(entry_type=2)
        elif value.type == "ascii":
            entry = LinSignalEncodingEntry_Value(entry_type=1)
        else:
            continue
        lse.entries.append(entry)
        session.add(entry)
    session.flush()
    return lse


__all__ = ["import_ncf_cpp"]
