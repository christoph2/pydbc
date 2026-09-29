#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Import LIN Description Files using the C++ LDF parser.

This module converts the parsed LDF AST into VNDB (SQLAlchemy) records,
mirroring the behavior of ``LdfListener`` but driven by the C++ parser.
"""

from __future__ import annotations

from pathlib import Path
from typing import Iterable, Optional

from pydbc.db import VNDB
from pydbc.db.model import (
    LinNetwork,
    LinMasterNode,
    LinSlaveNode,
    LinSignal,
    LinSignalRepresentation,
    LinSignalEncodingType,
    LinSignalEncodingEntry_Logical,
    LinSignalEncodingEntry_Physical,
    LinSignalEncodingEntry_Value,
    LinUnconditionalFrame,
    LinSporadicFrame,
    LinEventTriggeredFrame,
    LinScheduleTable,
    LinScheduleTable_Command_Frame,
    LinScheduleTable_Command_MasterReq,
    LinScheduleTable_Command_SlaveResp,
    LinScheduleTable_Command_AssignNad,
    LinScheduleTable_Command_ConditionalChangeNad,
    LinScheduleTable_Command_DataDump,
    LinScheduleTable_Command_SaveConfiguration,
    LinScheduleTable_Command_AssignFrameIdRange,
    LinScheduleTable_Command_FreeFormat,
    LinScheduleTable_Command_AssignFrameId,
    LinConfigurableFrame,
    LinFaultStateSignal,
    LinResponseErrorSignal,
    Vndb_Protocol,
)
from pydbc.types import BusType

try:
    from pydbc.cpp_ext.ldf_extension import LdfParser  # type: ignore
except Exception as exc:  # pragma: no cover - optional dependency
    LdfParser = None  # type: ignore


def _ensure_parser() -> type[LdfParser]:
    if LdfParser is None:
        raise RuntimeError(
            "C++ LDF parser extension is not available. Build the extension with build_ext.py"
        )
    return LdfParser


def import_ldf_cpp(
    file_path: str | Path,
    *,
    encoding: Optional[str] = None,
    debug: bool = False,
    logLevel: str = "WARN",
) -> object:
    """Import a .ldf file using the C++ LDF parser."""
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
        raise RuntimeError(f"LDF parsing failed: {messages}")

    vndb = VNDB.create(
        path.with_suffix(".vndb").as_posix(), debug=debug, logLevel=logLevel
    )
    session = vndb.session

    network = LinNetwork(
        name=vndb.dbname,
        protocol_version=ast.protocol_version,
        language_version=ast.language_version,
        speed=ast.speed,
        file_revision=ast.file_revision,
        channel_name=ast.channel_name,
    )
    session.add(network)
    session.add(Vndb_Protocol(network=network, name=BusType.LIN.name, specific=None))
    session.flush()

    nodes = _insert_nodes(session, ast.nodes)
    signals = _insert_signals(session, ast.signals, nodes)
    _insert_diagnostic_signals(session, ast.diagnostic_signals, nodes, signals)
    frames = _insert_frames(session, ast.frames, nodes, signals)
    _insert_sporadic_frames(session, ast.sporadic_frames, frames)
    _insert_event_triggered_frames(session, ast.event_triggered_frames, frames, nodes)
    _insert_node_attributes(session, ast.node_attributes, nodes, frames, signals)
    _insert_schedule_tables(session, ast.schedule_tables, frames, nodes)
    _insert_signal_encodings(session, ast.signal_encoding_types)
    _insert_signal_representations(session, ast.signal_representations, signals)

    session.commit()
    return session


def _insert_nodes(session, nodes_def) -> dict[str, object]:
    nodes: dict[str, object] = {}
    master = LinMasterNode(
        name=nodes_def.master,
        timebase=nodes_def.time_base,
        jitter=nodes_def.jitter,
        bit_length=nodes_def.bit_length,
        tolerant=nodes_def.tolerant,
    )
    session.add(master)
    session.flush()
    nodes[nodes_def.master] = master
    for slave_name in nodes_def.slaves:
        slave = LinSlaveNode(name=slave_name)
        session.add(slave)
        session.flush()
        nodes[slave_name] = slave
    session.flush()
    return nodes


def _insert_signals(session, signals, nodes) -> dict[str, LinSignal]:
    out: dict[str, LinSignal] = {}
    for sig in signals:
        publisher = nodes[sig.published_by]
        if sig.init_value.is_array:
            init_val = sig.init_value.array_values
        else:
            init_val = sig.init_value.scalar
        signal = LinSignal(
            name=sig.name,
            signal_size=sig.size,
            init_value=init_val,
            publisher=publisher,
        )
        session.add(signal)
        for subscriber_name in sig.subscribed_by:
            subscriber = nodes.get(subscriber_name)
            if subscriber is not None:
                signal.subscribers.append(subscriber)
        session.flush()
        out[sig.name] = signal
    return out


def _insert_diagnostic_signals(session, diag_signals, nodes, signals) -> None:
    for diag in diag_signals:
        if diag.name in signals:
            continue
        publisher = next(iter(nodes.values()))
        if diag.init_value.is_array:
            init_val = diag.init_value.array_values
        else:
            init_val = diag.init_value.scalar
        signal = LinSignal(
            name=diag.name,
            signal_size=diag.size,
            init_value=init_val,
            publisher=publisher,
        )
        session.add(signal)
        signals[diag.name] = signal
    session.flush()


def _insert_frames(session, frames, nodes, signals) -> dict[str, LinUnconditionalFrame]:
    out: dict[str, LinUnconditionalFrame] = {}
    for frame in frames:
        publisher = nodes[frame.published_by]
        msg = LinUnconditionalFrame(
            name=frame.name,
            frame_id=frame.frame_id,
            size=frame.frame_size,
            publisher=publisher,
        )
        session.add(msg)
        session.flush()
        for sig in frame.signals:
            signal = signals.get(sig.signal_name)
            if signal is not None:
                msg.add_signal(signal, sig.signal_offset)
        out[frame.name] = msg
    session.flush()
    return out


def _insert_sporadic_frames(session, sporadic_frames, frames) -> None:
    for sf in sporadic_frames:
        lsf = LinSporadicFrame(name=sf.name)
        session.add(lsf)
        session.flush()
        for frame_name in sf.frame_names:
            frame = frames.get(frame_name)
            if frame is not None:
                lsf.associated_frames.append(frame)
    session.flush()


def _insert_event_triggered_frames(session, event_frames, frames, nodes) -> None:
    master_node = next(iter(nodes.values()))
    for ef in event_frames:
        etf = LinEventTriggeredFrame(
            name=ef.name,
            master_node=master_node,
            frame_id=ef.frame_id,
        )
        session.add(etf)
        for frame_name in ef.frame_names:
            frame = frames.get(frame_name)
            if frame is not None:
                etf.associated_frames.append(frame)
    session.flush()


def _insert_node_attributes(session, attrs, nodes, frames, signals) -> None:
    configurable_frames: dict[str, list[LinConfigurableFrame]] = {}
    fault_state_signals: dict[str, list[LinFaultStateSignal]] = {}
    response_error_signals: dict[str, LinResponseErrorSignal] = {}
    for attr in attrs:
        node = nodes.get(attr.name)
        if node is None:
            continue
        node.protocol_version = attr.version
        node.configured_NAD = attr.configured_nad
        node.initial_NAD = attr.initial_nad
        node.product_id = (
            attr.product_id.supplier_id,
            attr.product_id.function_id,
            attr.product_id.variant or 0,
        )
        node.p2_min = attr.p2_min
        node.st_min = attr.st_min
        node.n_as_timeout = attr.n_as_timeout
        node.n_cr_timeout = attr.n_cr_timeout
        node.response_tolerance = attr.response_tolerance

        if attr.configurable_frames:
            configurable_frames[attr.name] = []
            for cfg in attr.configurable_frames:
                frame = frames.get(cfg.frame_name)
                if frame is None:
                    continue
                cf = LinConfigurableFrame(
                    node=node, frame=frame, identifier=cfg.message_id
                )
                session.add(cf)
                configurable_frames[attr.name].append(cf)

        if attr.fault_state_signals:
            fault_state_signals[attr.name] = []
            for fs in attr.fault_state_signals:
                signal = signals.get(fs)
                if signal is None:
                    continue
                lfs = LinFaultStateSignal(node=node, signal=signal)
                session.add(lfs)
                fault_state_signals[attr.name].append(lfs)

        if attr.response_error_signal:
            signal = signals.get(attr.response_error_signal)
            if signal is not None:
                res = LinResponseErrorSignal(node=node, signal=signal)
                session.add(res)
                response_error_signals[attr.name] = res
    session.flush()


def _insert_schedule_tables(session, schedule_tables, frames, nodes) -> None:
    for table in schedule_tables:
        lst = LinScheduleTable(name=table.name)
        session.add(lst)
        session.flush()
        for cmd in table.commands:
            entry = _create_schedule_entry(cmd, frames, nodes)
            if entry is None:
                continue
            session.add(entry)
            lst.commands.append(entry)
        session.flush()


def _create_schedule_entry(cmd, frames, nodes):
    if cmd.type == "Frame":
        frame = frames.get(cmd.frame_name)
        if frame is None:
            return None
        return LinScheduleTable_Command_Frame(frame_time=cmd.frame_time, frame=frame)
    if cmd.type == "MasterReq":
        return LinScheduleTable_Command_MasterReq(frame_time=cmd.frame_time)
    if cmd.type == "SlaveResp":
        return LinScheduleTable_Command_SlaveResp(frame_time=cmd.frame_time)
    if cmd.type == "AssignNAD":
        node = nodes.get(cmd.node_name)
        if node is None:
            return None
        return LinScheduleTable_Command_AssignNad(frame_time=cmd.frame_time, node=node)
    if cmd.type == "ConditionalChangeNAD":
        return LinScheduleTable_Command_ConditionalChangeNad(
            frame_time=cmd.frame_time,
            nad=cmd.nad,
            id=cmd.id,
            byte=cmd.byte,
            mask=cmd.mask,
            inv=cmd.inv,
            new_nad=cmd.new_nad,
        )
    if cmd.type == "DataDump":
        node = nodes.get(cmd.node_name)
        if node is None:
            return None
        data = list(cmd.data) + [0] * (5 - len(cmd.data))
        return LinScheduleTable_Command_DataDump(
            frame_time=cmd.frame_time,
            node=node,
            d1=data[0],
            d2=data[1],
            d3=data[2],
            d4=data[3],
            d5=data[4],
        )
    if cmd.type == "SaveConfiguration":
        node = nodes.get(cmd.node_name)
        if node is None:
            return None
        return LinScheduleTable_Command_SaveConfiguration(
            frame_time=cmd.frame_time, node=node
        )
    if cmd.type == "AssignFrameIdRange":
        node = nodes.get(cmd.node_name)
        if node is None:
            return None
        return LinScheduleTable_Command_AssignFrameIdRange(
            frame_time=cmd.frame_time,
            node=node,
            frame_index=cmd.frame_index,
            frame_pid1=cmd.pid1,
            frame_pid2=cmd.pid2,
            frame_pid3=cmd.pid3,
            frame_pid4=cmd.pid4,
        )
    if cmd.type == "FreeFormat":
        data = list(cmd.data) + [0] * (8 - len(cmd.data))
        return LinScheduleTable_Command_FreeFormat(
            frame_time=cmd.frame_time,
            d1=data[0],
            d2=data[1],
            d3=data[2],
            d4=data[3],
            d5=data[4],
            d6=data[5],
            d7=data[6],
            d8=data[7],
        )
    if cmd.type == "AssignFrameId":
        node = nodes.get(cmd.node_name)
        frame = frames.get(cmd.frame_name)
        if node is None or frame is None:
            return None
        return LinScheduleTable_Command_AssignFrameId(
            frame_time=cmd.frame_time, node=node, frame=frame
        )
    return None


def _insert_signal_encodings(session, encodings) -> None:
    for enc in encodings:
        lse = LinSignalEncodingType(name=enc.name)
        session.add(lse)
        for value in enc.values:
            text = _normalize_text(value.text)
            if value.value_type == "logical":
                entry = LinSignalEncodingEntry_Logical(
                    signal_value=value.signal_value, text_info=text
                )
            elif value.value_type == "range":
                entry = LinSignalEncodingEntry_Physical(
                    min_value=value.min_value,
                    max_value=value.max_value,
                    scale=value.scale,
                    offset=value.offset,
                    text_info=text,
                )
            elif value.value_type == "bcd":
                entry = LinSignalEncodingEntry_Value(entry_type=2)
            elif value.value_type == "ascii":
                entry = LinSignalEncodingEntry_Value(entry_type=1)
            else:
                continue
            lse.entries.append(entry)
            session.add(entry)
        session.flush()


def _insert_signal_representations(session, reps, signals) -> None:
    for rep in reps:
        lse = (
            session.query(LinSignalEncodingType)
            .filter_by(name=rep.encoding_name)
            .first()
        )
        if lse is None:
            continue
        for signal_name in rep.signal_names:
            signal = signals.get(signal_name)
            if signal is None:
                continue
            session.add(
                LinSignalRepresentation(signal_encoding_type=lse, signal=signal)
            )
    session.flush()


def _normalize_text(value: object) -> str | None:
    if value is None:
        return None
    if isinstance(value, bytes):
        return value.decode("latin-1", errors="replace")
    if isinstance(value, str):
        return value
    return str(value)


__all__ = ["import_ldf_cpp"]
