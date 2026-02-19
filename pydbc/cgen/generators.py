#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Code generators for standalone applications using Mako templates.

This module provides two generators:
- MicroPython CAN application (Python script) using machine.CAN or pyb.CAN depending on platform.
- Linux SocketCAN C source file with simple encode/decode and send/recv demo.

Both generators work from an SQLAlchemy session populated by pydbc (either
created via DBCCreator or returned by ParserWrapper/DbcListener). No runtime
DB access is required by the generated code; all message/signal metadata is
embedded at generation time.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Dict, Any, Iterable, Tuple
import pkgutil

from sqlalchemy.orm import Session

from pydbc.db.model import (
    Message,
    Message_Signal,
    Signal,
    LinNetwork,
    LinMasterNode,
    LinSlaveNode,
    LinSignal,
    LinUnconditionalFrame,
    LinSignalRepresentation,
    LinSignalEncodingEntry_Physical,
    LinSignalEncodingEntry_Logical,
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
    LinSporadicFrame,
    LinEventTriggeredFrame,
    LinConfigurableFrame,
)
from pydbc.template import renderTemplateFromText


@dataclass
class CGSignal:
    name: str
    start_bit: int
    size: int
    little_endian: bool
    signed: bool
    factor: float
    offset: float
    minimum: float
    maximum: float


@dataclass
class CGMessage:
    name: Optional[str]
    message_id: int
    dlc: int
    signals: List[CGSignal]


@dataclass
class CGLinSignalEncodingPhysical:
    min_value: Optional[float]
    max_value: Optional[float]
    scale: float
    offset: float
    text_info: Optional[str]


@dataclass
class CGLinSignalEncodingLogical:
    signal_value: float
    text_info: Optional[str]


@dataclass
class CGLinSignal:
    name: str
    size: int
    start_bit: int
    signed: bool
    init_value: int
    factor: float
    offset: float
    minimum: Optional[float]
    maximum: Optional[float]
    publisher: Optional[str]
    subscribers: List[str]
    physical_entries: List[CGLinSignalEncodingPhysical]
    logical_entries: List[CGLinSignalEncodingLogical]


@dataclass
class CGLinFrame:
    name: str
    frame_id: int
    pid: int
    dlc: int
    publisher: Optional[str]
    signals: List[CGLinSignal]


@dataclass
class CGLinScheduleCommand:
    command_type: str
    frame_time: float
    frame_name: Optional[str]
    node_name: Optional[str]
    params: Dict[str, Any]


@dataclass
class CGLinScheduleTable:
    name: str
    commands: List[CGLinScheduleCommand]


@dataclass
class CGLinSporadicFrame:
    name: str
    frame_id: int
    pid: int
    associated_frames: List[str]


@dataclass
class CGLinEventTriggeredFrame:
    name: str
    frame_id: int
    pid: int
    associated_frames: List[str]
    collision_resolving_schedule: Optional[str]


@dataclass
class CGLinConfigurableFrame:
    node_name: str
    frame_name: str
    identifier: Optional[int]


@dataclass
class CGLinNode:
    name: str
    role: str
    configured_nad: Optional[int]
    initial_nad: Optional[int]


def _collect_messages(
    session: Session, only: Optional[Iterable[str]] = None
) -> List[CGMessage]:
    q = session.query(Message)
    if only:
        q = q.filter(Message.name.in_(list(only)))
    msgs: List[CGMessage] = []
    for m in q.all():
        sigs: List[CGSignal] = []
        for ms in m.message_signals:
            s: Signal = ms.signal
            sigs.append(
                CGSignal(
                    name=s.name,
                    start_bit=ms.offset,
                    size=s.bitsize,
                    little_endian=True if (s.byteorder == 1) else False,
                    signed=(s.sign == 0),  # 0=signed, 1=unsigned in current model
                    factor=s.formula_factor or 1.0,
                    offset=s.formula_offset or 0.0,
                    minimum=float(s.minimum) if s.minimum is not None else 0.0,
                    maximum=float(s.maximum) if s.maximum is not None else 0.0,
                )
            )
        msgs.append(
            CGMessage(
                name=m.name,
                message_id=m.message_id or 0,
                dlc=m.dlc,
                signals=sigs,
            )
        )
    # Sort for stable output
    msgs.sort(key=lambda x: (x.message_id, x.name or ""))
    for msg in msgs:
        msg.signals.sort(key=lambda s: s.start_bit)
    return msgs


def _compute_lin_pid(frame_id: int) -> int:
    fid = frame_id & 0x3F
    p0 = ((fid >> 0) ^ (fid >> 1) ^ (fid >> 2) ^ (fid >> 4)) & 0x1
    p1 = (~((fid >> 1) ^ (fid >> 3) ^ (fid >> 4) ^ (fid >> 5))) & 0x1
    return fid | (p0 << 6) | (p1 << 7)


def _normalize_lin_init_value(value: Any) -> int:
    if isinstance(value, (list, tuple)):
        return int(value[0]) if value else 0
    return int(value)


def _collect_lin_signal_encodings(
    session: Session, signal: LinSignal
) -> Tuple[List[CGLinSignalEncodingPhysical], List[CGLinSignalEncodingLogical]]:
    physical_entries: List[CGLinSignalEncodingPhysical] = []
    logical_entries: List[CGLinSignalEncodingLogical] = []
    reps = session.query(LinSignalRepresentation).filter_by(signal=signal).all()
    for rep in reps:
        entries = rep.signal_encoding_type.entries if rep.signal_encoding_type else []
        for entry in entries or []:
            if isinstance(entry, LinSignalEncodingEntry_Physical):
                physical_entries.append(
                    CGLinSignalEncodingPhysical(
                        min_value=entry.min_value,
                        max_value=entry.max_value,
                        scale=entry.scale if entry.scale is not None else 1.0,
                        offset=entry.offset if entry.offset is not None else 0.0,
                        text_info=entry.text_info,
                    )
                )
            elif isinstance(entry, LinSignalEncodingEntry_Logical):
                logical_entries.append(
                    CGLinSignalEncodingLogical(
                        signal_value=entry.signal_value,
                        text_info=entry.text_info,
                    )
                )
    return physical_entries, logical_entries


def _collect_lin_data(session: Session) -> Dict[str, Any]:
    signal_cache: Dict[int, CGLinSignal] = {}

    def build_signal(signal: LinSignal, start_bit: int) -> CGLinSignal:
        cached = signal_cache.get(signal.lin_signal_id)
        if cached and cached.start_bit == start_bit:
            return cached
        physical_entries, logical_entries = _collect_lin_signal_encodings(
            session, signal
        )
        if physical_entries:
            primary = physical_entries[0]
            factor = primary.scale
            offset = primary.offset
            minimum = primary.min_value
            maximum = primary.max_value
        else:
            factor = 1.0
            offset = 0.0
            minimum = None
            maximum = None
        cg = CGLinSignal(
            name=signal.name,
            size=signal.bitsize,
            start_bit=start_bit,
            signed=(signal.sign == 0),
            init_value=_normalize_lin_init_value(signal.init_value),
            factor=factor,
            offset=offset,
            minimum=minimum,
            maximum=maximum,
            publisher=signal.publisher.name if signal.publisher else None,
            subscribers=[s.name for s in signal.subscribers],
            physical_entries=physical_entries,
            logical_entries=logical_entries,
        )
        signal_cache[signal.lin_signal_id] = cg
        return cg

    unconditional_frames: List[CGLinFrame] = []
    for frame in session.query(LinUnconditionalFrame).all():
        if frame.__class__ is not LinUnconditionalFrame:
            continue
        sigs: List[CGLinSignal] = []
        for fs in frame.frame_signals:
            sigs.append(build_signal(fs.signal, fs.signal_offset))
        unconditional_frames.append(
            CGLinFrame(
                name=frame.name,
                frame_id=frame.frame_id,
                pid=_compute_lin_pid(frame.frame_id),
                dlc=frame.dlc,
                publisher=frame.publisher.name if frame.publisher else None,
                signals=sigs,
            )
        )

    sporadic_frames: List[CGLinSporadicFrame] = []
    for frame in session.query(LinSporadicFrame).all():
        sporadic_frames.append(
            CGLinSporadicFrame(
                name=frame.name,
                frame_id=frame.frame_id,
                pid=_compute_lin_pid(frame.frame_id),
                associated_frames=[f.name for f in frame.associated_frames],
            )
        )

    event_frames: List[CGLinEventTriggeredFrame] = []
    for frame in session.query(LinEventTriggeredFrame).all():
        event_frames.append(
            CGLinEventTriggeredFrame(
                name=frame.name,
                frame_id=frame.frame_id,
                pid=_compute_lin_pid(frame.frame_id),
                associated_frames=[f.name for f in frame.associated_frames],
                collision_resolving_schedule=(
                    frame.collision_resolving_schedule_table.name
                    if frame.collision_resolving_schedule_table
                    else None
                ),
            )
        )

    configurable_frames: List[CGLinConfigurableFrame] = []
    for cfg in session.query(LinConfigurableFrame).all():
        configurable_frames.append(
            CGLinConfigurableFrame(
                node_name=cfg.node.name if cfg.node else "",
                frame_name=cfg.frame.name if cfg.frame else "",
                identifier=cfg.identifier,
            )
        )

    schedule_tables: List[CGLinScheduleTable] = []
    for table in session.query(LinScheduleTable).all():
        commands: List[CGLinScheduleCommand] = []
        for cmd in table.commands:
            command_type = cmd.__class__.__name__.replace(
                "LinScheduleTable_Command_", ""
            )
            frame_name = None
            node_name = None
            params: Dict[str, Any] = {}
            if isinstance(cmd, LinScheduleTable_Command_Frame):
                frame_name = cmd.frame.name if cmd.frame else None
            elif isinstance(cmd, LinScheduleTable_Command_AssignNad):
                node_name = cmd.node.name if cmd.node else None
            elif isinstance(cmd, LinScheduleTable_Command_ConditionalChangeNad):
                params = {
                    "nad": cmd.nad,
                    "id": cmd.id,
                    "byte": cmd.byte,
                    "mask": cmd.mask,
                    "inv": cmd.inv,
                    "new_nad": cmd.new_nad,
                }
            elif isinstance(cmd, LinScheduleTable_Command_DataDump):
                node_name = cmd.node.name if cmd.node else None
                params = {
                    "d1": cmd.d1,
                    "d2": cmd.d2,
                    "d3": cmd.d3,
                    "d4": cmd.d4,
                    "d5": cmd.d5,
                }
            elif isinstance(cmd, LinScheduleTable_Command_SaveConfiguration):
                node_name = cmd.node.name if cmd.node else None
            elif isinstance(cmd, LinScheduleTable_Command_AssignFrameIdRange):
                node_name = cmd.node.name if cmd.node else None
                params = {
                    "frame_index": cmd.frame_index,
                    "frame_pid1": cmd.frame_pid1,
                    "frame_pid2": cmd.frame_pid2,
                    "frame_pid3": cmd.frame_pid3,
                    "frame_pid4": cmd.frame_pid4,
                }
            elif isinstance(cmd, LinScheduleTable_Command_FreeFormat):
                params = {
                    "d1": cmd.d1,
                    "d2": cmd.d2,
                    "d3": cmd.d3,
                    "d4": cmd.d4,
                    "d5": cmd.d5,
                    "d6": cmd.d6,
                    "d7": cmd.d7,
                    "d8": cmd.d8,
                }
            elif isinstance(cmd, LinScheduleTable_Command_AssignFrameId):
                node_name = cmd.node.name if cmd.node else None
                frame_name = cmd.frame.name if cmd.frame else None
            elif isinstance(
                cmd,
                (
                    LinScheduleTable_Command_MasterReq,
                    LinScheduleTable_Command_SlaveResp,
                ),
            ):
                pass

            commands.append(
                CGLinScheduleCommand(
                    command_type=command_type,
                    frame_time=cmd.frame_time,
                    frame_name=frame_name,
                    node_name=node_name,
                    params=params,
                )
            )
        schedule_tables.append(CGLinScheduleTable(name=table.name, commands=commands))

    nodes: List[CGLinNode] = []
    master = session.query(LinMasterNode).first()
    if master:
        nodes.append(
            CGLinNode(
                name=master.name,
                role="master",
                configured_nad=None,
                initial_nad=None,
            )
        )
    for slave in session.query(LinSlaveNode).all():
        nodes.append(
            CGLinNode(
                name=slave.name,
                role="slave",
                configured_nad=slave.configured_NAD,
                initial_nad=slave.initial_NAD,
            )
        )

    network = session.query(LinNetwork).first()
    return {
        "network_name": network.name if network else None,
        "nodes": nodes,
        "unconditional_frames": unconditional_frames,
        "sporadic_frames": sporadic_frames,
        "event_triggered_frames": event_frames,
        "configurable_frames": configurable_frames,
        "schedule_tables": schedule_tables,
    }


class MicroPythonCanAppGenerator:
    """Generates a standalone MicroPython CAN app (.py) with encode/decode helpers.

    Usage:
        gen = MicroPythonCanAppGenerator(session)
        code = gen.render(only=["EngineData"])  # optional filter
        Path("micropython_app.py").write_text(code, encoding="utf-8")
    """

    TEMPLATE = pkgutil.get_data("pydbc", "cgen/templates/micropython_can.py.tmpl")

    def __init__(self, session: Session):
        self._session = session

    def render(
        self, only: Optional[Iterable[str]] = None, app_name: str = "pydbc_mpy_app"
    ) -> str:
        msgs = _collect_messages(self._session, only)
        ns: Dict[str, Any] = {
            "app_name": app_name,
            "messages": msgs,
        }
        text = (
            self.TEMPLATE.decode("utf-8")
            if isinstance(self.TEMPLATE, (bytes, bytearray))
            else str(self.TEMPLATE)
        )
        return renderTemplateFromText(text, ns, encoding="utf-8")


class SocketCanCGenerator:
    """Generates a standalone Linux SocketCAN C program (.c) with encode/decode helpers.

    Usage:
        gen = SocketCanCGenerator(session)
        code = gen.render(only=["EngineData"])  # optional filter
        Path("socketcan_app.c").write_text(code, encoding="utf-8")
    """

    TEMPLATE = pkgutil.get_data("pydbc", "cgen/templates/socketcan.c.tmpl")

    def __init__(self, session: Session):
        self._session = session

    def render(
        self,
        only: Optional[Iterable[str]] = None,
        program_name: str = "pydbc_socketcan_app",
    ) -> str:
        msgs = _collect_messages(self._session, only)
        ns: Dict[str, Any] = {
            "program_name": program_name,
            "messages": msgs,
        }
        text = (
            self.TEMPLATE.decode("utf-8")
            if isinstance(self.TEMPLATE, (bytes, bytearray))
            else str(self.TEMPLATE)
        )
        return renderTemplateFromText(text, ns, encoding="utf-8")


class PythonCanAppGenerator:
    """Generates eine standalone Python-Anwendung (.py) auf Basis von python-can.

    Nutzung:
        gen = PythonCanAppGenerator(session)
        code = gen.render(only=["EngineData"], app_name="pydbc_python_can_app")
        Path("python_can_app.py").write_text(code, encoding="utf-8")
    """

    TEMPLATE = pkgutil.get_data("pydbc", "cgen/templates/python_can.py.tmpl")

    def __init__(self, session: Session):
        self._session = session

    def render(
        self,
        only: Optional[Iterable[str]] = None,
        app_name: str = "pydbc_python_can_app",
    ) -> str:
        msgs = _collect_messages(self._session, only)
        ns: Dict[str, Any] = {
            "app_name": app_name,
            "messages": msgs,
        }
        text = (
            self.TEMPLATE.decode("utf-8")
            if isinstance(self.TEMPLATE, (bytes, bytearray))
            else str(self.TEMPLATE)
        )
        return renderTemplateFromText(text, ns, encoding="utf-8")


class LinGenericGenerator:
    """Generiert generischen LIN-Code (Python + C++) für Encode/Decode, Scheduling-Metadaten.

    Nutzung:
        gen = LinGenericGenerator(session)
        py_code = gen.render_python(module_name="lin_generated")
        cpp_code = gen.render_cpp(header_name="lin_generated.hpp")
    """

    TEMPLATE_PY = pkgutil.get_data("pydbc", "cgen/templates/lin_generic.py.tmpl")
    TEMPLATE_HPP = pkgutil.get_data("pydbc", "cgen/templates/lin_generic.hpp.tmpl")

    def __init__(self, session: Session):
        self._session = session

    def render_python(self, module_name: str = "lin_generated") -> str:
        data = _collect_lin_data(self._session)
        ns: Dict[str, Any] = {
            "module_name": module_name,
            **data,
        }
        text = (
            self.TEMPLATE_PY.decode("utf-8")
            if isinstance(self.TEMPLATE_PY, (bytes, bytearray))
            else str(self.TEMPLATE_PY)
        )
        return renderTemplateFromText(text, ns, encoding="utf-8")

    def render_cpp(self, header_name: str = "lin_generated.hpp") -> str:
        data = _collect_lin_data(self._session)
        ns: Dict[str, Any] = {
            "header_name": header_name,
            **data,
        }
        text = (
            self.TEMPLATE_HPP.decode("utf-8")
            if isinstance(self.TEMPLATE_HPP, (bytes, bytearray))
            else str(self.TEMPLATE_HPP)
        )
        return renderTemplateFromText(text, ns, encoding="utf-8")
