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
from typing import List, Optional, Dict, Any, Iterable
import pkgutil

from sqlalchemy.orm import Session

from pydbc.db.model import Message, Message_Signal, Signal
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


def _collect_messages(session: Session, only: Optional[Iterable[str]] = None) -> List[CGMessage]:
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

    def render(self, only: Optional[Iterable[str]] = None, app_name: str = "pydbc_mpy_app") -> str:
        msgs = _collect_messages(self._session, only)
        ns: Dict[str, Any] = {
            "app_name": app_name,
            "messages": msgs,
        }
        text = self.TEMPLATE.decode("utf-8") if isinstance(self.TEMPLATE, (bytes, bytearray)) else str(self.TEMPLATE)
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

    def render(self, only: Optional[Iterable[str]] = None, program_name: str = "pydbc_socketcan_app") -> str:
        msgs = _collect_messages(self._session, only)
        ns: Dict[str, Any] = {
            "program_name": program_name,
            "messages": msgs,
        }
        text = self.TEMPLATE.decode("utf-8") if isinstance(self.TEMPLATE, (bytes, bytearray)) else str(self.TEMPLATE)
        return renderTemplateFromText(text, ns, encoding="utf-8")
