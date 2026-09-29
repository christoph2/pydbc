#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from pathlib import Path
import shutil
import pytest

import pydbc.db.model as model
from pydbc.dbc_cpp_importer import import_dbc_cpp

DBC_CONTENT = """
VERSION "1.0"

NS_ :
    NS_DESC_
    CM_
    BA_DEF_
    BA_
    VAL_
    CAT_DEF_
    CAT_
    FILTER
    BA_DEF_DEF_
    EV_DATA_
    ENVVAR_DATA_
    SG_MUL_VAL_
    BA_DEF_SGTYPE_
    BA_SGTYPE_
    SIG_TYPE_REF_
    VAL_TABLE_
    SIG_GROUP_
    SIG_VALTYPE_
    SIGTYPE_VALTYPE_
    BO_TX_BU_
    BA_DEF_REL_
    BA_REL_
    BA_DEF_DEF_REL_
    BU_SG_REL_
    BU_EV_REL_
    BU_BO_REL_
    SG_MUL_VAL_

BS_:

BU_: Engine Gateway Dashboard

BO_ 781 VehicleData: 8 Engine
 SG_ Speed : 0|16@1+ (0.01,0) [0|655.35] "km/h" Gateway,Dashboard
 SG_ RPM : 16|16@1+ (1,0) [0|8000] "rpm" Gateway,Dashboard

BO_ 100 Status: 1 Gateway
 SG_ Temperature : 0|8@1+ (1,-40) [-40|215] "C" Dashboard

CM_ BU_ Engine "The engine control unit";
CM_ BO_ 781 "Main vehicle data message";
CM_ SG_ 781 Speed "Vehicle speed in km/h";

BA_DEF_ BO_  "GenMsgCycleTime" INT 0 10000;
BA_DEF_ DEF_ "BusType" STRING ;
BA_DEF_DEF_ "GenMsgCycleTime" 100;
BA_DEF_DEF_ "BusType" "CAN";

BA_ "GenMsgCycleTime" BO_ 781 50;
"""


def test_dbc_cpp_importer(tmp_path: Path):
    dbc_file = tmp_path / "test.dbc"
    dbc_file.write_text(DBC_CONTENT, encoding="latin-1")

    session = import_dbc_cpp(dbc_file)

    # Check nodes
    nodes = session.query(model.Node).all()
    node_names = [n.name for n in nodes]
    assert "Engine" in node_names
    assert "Gateway" in node_names
    assert "Dashboard" in node_names
    assert "Vector__XXX" in node_names

    engine_node = session.query(model.Node).filter(model.Node.name == "Engine").one()
    assert engine_node.comment == "The engine control unit"

    # Check messages
    messages = session.query(model.Message).all()
    assert len(messages) == 2
    msg_781 = session.query(model.Message).filter(model.Message.message_id == 781).one()
    assert msg_781.name == "VehicleData"
    assert msg_781.dlc == 8
    assert msg_781.comment == "Main vehicle data message"

    # Check signals
    signals = msg_781.signals
    assert len(signals) == 2
    speed_sig = [s for s in signals if s.name == "Speed"][0]
    assert speed_sig.bitsize == 16
    assert speed_sig.unit == "km/h"
    assert speed_sig.formula_factor == 0.01
    assert speed_sig.comment == "Vehicle speed in km/h"

    # Check Attributes
    attr_defs = session.query(model.Attribute_Definition).all()
    attr_names = [ad.name for ad in attr_defs]
    assert "GenMsgCycleTime" in attr_names
    assert "BusType" in attr_names

    # Check Attribute Value
    val = (
        session.query(model.Attribute_Value)
        .join(model.Attribute_Definition)
        .filter(
            model.Attribute_Definition.name == "GenMsgCycleTime",
            model.Attribute_Value.object_id == msg_781.rid,
        )
        .one()
    )
    assert val.num_value == 50
