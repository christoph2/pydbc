#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
python-can integration helpers for pyDBC.

This module provides:
- encode_message: Pack physical signal values into a CAN frame payload
  according to the DBC data stored in the VNDB (SQLAlchemy session).
- decode_message: Unpack a CAN frame payload back to physical signal values.
- Optional convenience sender/receiver classes that use python-can if installed.

Notes/assumptions:
- Currently supports little-endian (Intel) signals (Signal.byteorder == 1).
  Big-endian (Motorola) signals raise NotImplementedError.
- Signal.sign: In the current model, sign==1 is treated as unsigned, 0 as signed.
- Physical<->raw conversion uses: phys = raw * factor + offset
  and raw = round((phys - offset) / factor).

This module avoids a hard dependency on python-can. The Bus-related classes
attempt to import python-can at runtime and fail gracefully with clear messages
if it's not installed.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Tuple, Any, Optional, List

from sqlalchemy.orm import Session

from pydbc.db.model import Message, Message_Signal, Signal


@dataclass
class CompiledSignal:
    name: str
    start_bit: int  # bit offset in frame
    size: int       # bits
    little_endian: bool
    signed: bool
    factor: float
    offset: float
    minimum: float
    maximum: float


@dataclass
class CompiledMessage:
    message_id: int
    dlc: int
    name: Optional[str]
    signals: List[CompiledSignal]


def _compile_message(session: Session, message: Message) -> CompiledMessage:
    sigs: List[CompiledSignal] = []
    for ms in message.message_signals:
        sig: Signal = ms.signal
        if sig.byteorder not in (0, 1):
            raise ValueError(f"Unsupported byteorder {sig.byteorder} for signal {sig.name}")
        little = sig.byteorder == 1
        signed = (sig.sign == 0)  # treat 0 as signed, 1 as unsigned
        sigs.append(
            CompiledSignal(
                name=sig.name,
                start_bit=ms.offset,
                size=sig.bitsize,
                little_endian=little,
                signed=signed,
                factor=sig.formula_factor or 1.0,
                offset=sig.formula_offset or 0.0,
                minimum=sig.minimum if sig.minimum is not None else 0.0,
                maximum=sig.maximum if sig.maximum is not None else 0.0,
            )
        )
    return CompiledMessage(
        message_id=message.message_id or 0,
        dlc=message.dlc,
        name=message.name,
        signals=sigs,
    )


def get_message_by_name(session: Session, name: str) -> Message:
    msg = session.query(Message).filter_by(name=name).first()
    if not msg:
        raise KeyError(f"Message with name '{name}' not found")
    return msg


def get_message_by_id(session: Session, can_id: int) -> Message:
    msg = session.query(Message).filter_by(message_id=can_id).first()
    if not msg:
        raise KeyError(f"Message with ID 0x{can_id:X} not found")
    return msg


# --- Bit packing utilities (little-endian/Intel only) ---

def _insert_bits_le(buf: bytearray, start_bit: int, size: int, value: int) -> None:
    """Insert 'size' bits of 'value' into buf at little-endian start_bit.
    Little-endian here means the start_bit 0 is the LSB of byte 0, increasing upwards.
    """
    # Mask value to size bits
    if size <= 0:
        return
    mask = (1 << size) - 1
    value &= mask

    bit_pos = start_bit
    remaining = size
    while remaining > 0:
        byte_index = bit_pos // 8
        bit_index = bit_pos % 8
        bits_in_this_byte = min(remaining, 8 - bit_index)
        # Extract the chunk to write at current position
        chunk_mask = (1 << bits_in_this_byte) - 1
        chunk = value & chunk_mask
        # Clear target bits
        buf[byte_index] &= ~(chunk_mask << bit_index)
        # Write
        buf[byte_index] |= (chunk << bit_index)
        # Advance
        value >>= bits_in_this_byte
        remaining -= bits_in_this_byte
        bit_pos += bits_in_this_byte


def _extract_bits_le(buf: bytes, start_bit: int, size: int, signed: bool) -> int:
    if size <= 0:
        return 0
    bit_pos = start_bit
    remaining = size
    out = 0
    shift = 0
    while remaining > 0:
        byte_index = bit_pos // 8
        bit_index = bit_pos % 8
        bits_in_this_byte = min(remaining, 8 - bit_index)
        chunk_mask = (1 << bits_in_this_byte) - 1
        byte_val = buf[byte_index]
        chunk = (byte_val >> bit_index) & chunk_mask
        out |= (chunk << shift)
        remaining -= bits_in_this_byte
        bit_pos += bits_in_this_byte
        shift += bits_in_this_byte
    if signed:
        # sign-extend
        sign_bit = 1 << (size - 1)
        if out & sign_bit:
            out = out - (1 << size)
    return out


def _phys_to_raw(value: float, factor: float, offset: float, size: int, signed: bool) -> int:
    if factor == 0:
        # Avoid division by zero; treat as identity around offset
        raw = int(round(value - offset))
    else:
        raw = int(round((value - offset) / factor))
    # Clamp to representable range
    if signed:
        min_raw = -(1 << (size - 1))
        max_raw = (1 << (size - 1)) - 1
    else:
        min_raw = 0
        max_raw = (1 << size) - 1
    return max(min(raw, max_raw), min_raw)


def _raw_to_phys(raw: int, factor: float, offset: float) -> float:
    return raw * factor + offset


def encode_message(session: Session, message_name: str, signal_values: Dict[str, float]) -> Tuple[int, bytes, int]:
    """Encode a message by name into (can_id, data_bytes, dlc).

    Returns a tuple suitable for constructing a python-can Message:
    (arbitration_id, data, dlc)
    """
    msg = get_message_by_name(session, message_name)
    cm = _compile_message(session, msg)
    data = bytearray([0] * cm.dlc)

    # Place each signal
    for sig in cm.signals:
        if not sig.little_endian:
            raise NotImplementedError(
                f"Signal '{sig.name}' is big-endian (Motorola); not supported yet."
            )
        if sig.name not in signal_values:
            # Missing values default to 0 after scaling
            phys = 0.0
        else:
            phys = float(signal_values[sig.name])
        raw = _phys_to_raw(phys, sig.factor, sig.offset, sig.size, sig.signed)
        _insert_bits_le(data, sig.start_bit, sig.size, raw)

    return cm.message_id, bytes(data), cm.dlc


def decode_message(session: Session, can_id: int, data: bytes) -> Dict[str, Any]:
    """Decode a received CAN frame given arbitration id and data payload.

    Returns dict: {"message": name, "signals": {sig_name: physical_value, ...}}
    """
    msg = get_message_by_id(session, can_id)
    cm = _compile_message(session, msg)
    result: Dict[str, float] = {}

    for sig in cm.signals:
        if not sig.little_endian:
            raise NotImplementedError(
                f"Signal '{sig.name}' is big-endian (Motorola); not supported yet."
            )
        raw = _extract_bits_le(data, sig.start_bit, sig.size, sig.signed)
        phys = _raw_to_phys(raw, sig.factor, sig.offset)
        result[sig.name] = phys

    return {"message": cm.name or f"0x{cm.message_id:X}", "signals": result}


class PythonCanSender:
    """Simple sender using python-can Bus.

    Usage:
        sender = PythonCanSender(channel='vcan0', bustype='virtual')
        arb_id, data, dlc = encode_message(session, 'EngineData', {...})
        sender.send(arb_id, data)
    """

    def __init__(self, **bus_kwargs):
        try:
            import can  # type: ignore
        except Exception as exc:
            raise RuntimeError(
                "python-can is required for PythonCanSender. Install with 'pip install python-can'."
            ) from exc
        self._can = can
        self._bus = can.Bus(**bus_kwargs)

    def send(self, arbitration_id: int, data: bytes, is_extended_id: bool = False) -> None:
        msg = self._can.Message(
            arbitration_id=arbitration_id,
            is_extended_id=is_extended_id,
            data=data,
        )
        self._bus.send(msg)

    def shutdown(self) -> None:
        try:
            self._bus.shutdown()
        except Exception:
            pass


class PythonCanReceiver:
    """Simple receiver that decodes messages with a pydbc session.

    Example:
        rx = PythonCanReceiver(session, channel='vcan0', bustype='virtual')
        frame = rx.recv(timeout=1.0)
        if frame: print(rx.decode_frame(frame))
    """

    def __init__(self, session: Session, **bus_kwargs):
        try:
            import can  # type: ignore
        except Exception as exc:
            raise RuntimeError(
                "python-can is required for PythonCanReceiver. Install with 'pip install python-can'."
            ) from exc
        self._can = can
        self._bus = can.Bus(**bus_kwargs)
        self._session = session

    def recv(self, timeout: Optional[float] = None):
        return self._bus.recv(timeout=timeout)

    def decode_frame(self, frame) -> Dict[str, Any]:
        return decode_message(self._session, frame.arbitration_id, bytes(frame.data))

    def shutdown(self) -> None:
        try:
            self._bus.shutdown()
        except Exception:
            pass
