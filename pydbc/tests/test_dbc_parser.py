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

