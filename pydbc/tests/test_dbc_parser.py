#!/usr/bin/env python
# -*- coding: latin-1 -*-

"""
"""

import pytest

import pydbc.db.model as model
from pydbc.parser import ParserWrapper
from pydbc.dbcListener import DbcListener


def check_dummy_node(node):
    assert node.rid == 0
    assert node.comment == 'Dummy node for non-existent senders/receivers.'
    assert node.name == 'Vector__XXX'
    assert node.node_id == 0

def test_no_nodes():
    parser = ParserWrapper('dbc', 'nodes', DbcListener, debug = False)
    DATA = "BU_:"
    session = parser.parseFromString(DATA)
    res = session.query(model.Node).all()
    assert len(res) == 1
    check_dummy_node(res[0])

def test_one_nodes():
    parser = ParserWrapper('dbc', 'nodes', DbcListener, debug = False)
    DATA = "BU_: MECU"
    session = parser.parseFromString(DATA)
    res = session.query(model.Node).all()
    assert len(res) == 2
    check_dummy_node(res[0])
    assert res[1].name == "MECU"

def test_multiple_nodes():
    parser = ParserWrapper('dbc', 'nodes', DbcListener, debug = False)
    DATA = "BU_: MECU KSG BCU"
    session = parser.parseFromString(DATA)
    res = session.query(model.Node).all()
    assert len(res) == 4
    check_dummy_node(res[0])
    assert res[1].name == "MECU"
    assert res[2].name == "KSG"
    assert res[3].name == "BCU"

def test_errorous_node1():
    parser = ParserWrapper('dbc', 'nodes', DbcListener, debug = False)
    DATA = "BU_: MECU 0235 BCU"
    session = parser.parseFromString(DATA)
    res = session.query(model.Node).all()
    assert len(res) == 2
    check_dummy_node(res[0])
    assert res[1].name == "MECU"

def test_errorous_node2():
    parser = ParserWrapper('dbc', 'nodes', DbcListener, debug = False)
    DATA = "BU_: MECU BCU 0235"
    session = parser.parseFromString(DATA)
    res = session.query(model.Node).all()
    assert len(res) == 3
    check_dummy_node(res[0])
    assert res[1].name == "MECU"
    assert res[2].name == "BCU"

def test_message1():
    parser = ParserWrapper('dbc', 'messages', DbcListener, debug = False)
    DATA = """BO_ 781 VBOX_10: 8 Vector__XXX
            SG_ Link_Time : 47|24@0+ (0.01,0) [0|0] "Seconds" Vector__XXX
            SG_ Status_remote : 39|8@0+ (1,0) [0|0] "-" Vector__XXX
            SG_ Sep_Angle : 7|32@0- (1,0) [-180|180] "Deg" Vector__XXX"""
    session = parser.parseFromString(DATA)
    res = session.query(model.Message).all()
    assert len(res) == 1
    msg = res[0]
    msg.comment == None
    msg.rid == 1
    msg.name == 'VBOX_10'
    msg.message_id == 781
    msg.dlc == 8
    msg.sender == 0
    msg.type == 'Message'
    signals = msg.signals
    assert len(signals) == 3
    s0, s1, s2 = signals
    assert s0.comment == None
    assert s0.rid == 1
    assert s0.name == 'Link_Time'
    assert s0.bitsize == 24
    assert s0.byteorder == 0
    assert s0.sign == 1
    assert s0.valuetype == 0
    assert s0.formula_factor == 0.01
    assert s0.formula_offset == 0.0
    assert s0.minimum == 0.0
    assert s0.maximum == 0.0
    assert s0.unit == 'Seconds'
    assert s1.comment == None
    assert s1.rid == 2
    assert s1.name == 'Status_remote'
    assert s1.bitsize == 8
    assert s1.byteorder == 0
    assert s1.sign == 1
    assert s1.valuetype == 0
    assert s1.formula_factor == 1.0
    assert s1.formula_offset == 0.0
    assert s1.minimum == 0.0
    assert s1.maximum == 0.0
    assert s1.unit == '-'
    assert s2.comment == None
    assert s2.rid == 3
    assert s2.name == 'Sep_Angle'
    assert s2.bitsize == 32
    assert s2.byteorder == 0
    assert s2.sign == -1
    assert s2.valuetype == 0
    assert s2.formula_factor == 1.0
    assert s2.formula_offset == 0.0
    assert s2.minimum == -180.0
    assert s2.maximum == 180.0
    assert s2.unit == 'Deg'

def test_message_no_signals():
    parser = ParserWrapper('dbc', 'messages', DbcListener, debug = False)
    DATA = """BO_ 781 VBOX_10: 8 Vector__XXX"""
    session = parser.parseFromString(DATA)
    res = session.query(model.Message).all()
    assert len(res) == 1
    assert res[0].signals == []


def test_malformed_message_no_id():
    parser = ParserWrapper('dbc', 'messages', DbcListener, debug = False)
    DATA = """BO_ VBOX_10: 8 Vector__XXX"""
    session = parser.parseFromString(DATA)
    res = session.query(model.Message).all()
    assert len(res) == 1
    msg = res[0]
    assert msg.comment == None
    assert msg.rid == 1
    assert msg.name == 'VBOX_10'
    assert msg.message_id == None
    assert msg.dlc == 8
    assert msg.sender == 0
    assert msg.type == 'Message'

def test_malformed_message_wrong_id():
    parser = ParserWrapper('dbc', 'messages', DbcListener, debug = False)
    DATA = """BO_ ABC VBOX_10: 8 Vector__XXX"""
    session = parser.parseFromString(DATA)
    res = session.query(model.Message).all()
    assert len(res) == 1
    msg = res[0]
    assert msg.comment == None
    assert msg.rid == 1
    assert msg.name == 'ABC'
    assert msg.message_id == None
    assert msg.dlc == 8
    assert msg.sender == 0
    assert msg.type == 'Message'

def test_malformed_message_no_name():
    parser = ParserWrapper('dbc', 'messages', DbcListener, debug = False)
    DATA = """BO_ 781 : 8 Vector__XXX"""
    session = parser.parseFromString(DATA)
    res = session.query(model.Message).all()
    assert len(res) == 1
    msg = res[0]
    assert msg.comment == None
    assert msg.rid == 1
    assert msg.name == None
    assert msg.message_id == 781
    assert msg.dlc == 8
    assert msg.sender == 0
    assert msg.type == 'Message'

def test_invalid_signal1():
    parser = ParserWrapper('dbc', 'messages', DbcListener, debug = False)
    DATA = """
    BO_ 1600 Reporting_Message_640: 8 Vector__XXX
        SG_ Opto_IO_1 : 0|1@0+ (1,0) [0|0] "" Vector__XXX
        SG_ Analog_Input_1_(0-26.4V) : 15|8@0+ (0.103529,0) [0|26] "" Vector__XXX
    """
    session = parser.parseFromString(DATA)
    res = session.query(model.Message).all()
    assert len(res) == 1
    msg = res[0]
    assert len(msg.signals) == 2
    s0, s1 = msg.signals
    assert s0.comment == None
    assert s0.rid == 1
    assert s0.name == 'Opto_IO_1'
    assert s0.bitsize == 1
    assert s0.byteorder == 0
    assert s0.sign == 1
    assert s0.valuetype == 0
    assert s0.formula_factor == 1.0
    assert s0.formula_offset == 0.0
    assert s0.minimum == 0.0
    assert s0.maximum == 0.0
    assert s0.unit == ''
    assert s1.comment == None
    assert s1.rid == 2
    assert s1.name == 'Analog_Input_1_'
    assert s1.bitsize == 0
    assert s1.byteorder == 0
    assert s1.sign == 1
    assert s1.valuetype == 0
    assert s1.formula_factor == 1.0
    assert s1.formula_offset == 0.0
    assert s1.minimum == 0.0
    assert s1.maximum == 0.0
    assert s1.unit == None
