#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pathlib import Path
import shutil

import pytest

import pydbc.db.model as model

LDF_FILE = Path(__file__).parents[1] / "examples" / "ldf-files" / "IBS_200X_P_24V.ldf"


def _require_ldf_extension():
    return pytest.importorskip("pydbc.cpp_ext.ldf_extension")


def test_ldf_cpp_parser_ast():
    ldf_extension = _require_ldf_extension()
    parser = ldf_extension.LdfParser(str(LDF_FILE))
    ast = parser.parse()
    assert parser.get_diagnostics() == []
    assert ast.protocol_version == "2.0"
    assert ast.language_version == "2.0"
    assert ast.nodes.master == "SG"
    assert "IBS" in ast.nodes.slaves
    assert len(ast.signals) > 0
    assert len(ast.frames) > 0
    assert len(ast.schedule_tables) > 0


def test_ldf_cpp_importer(tmp_path: Path):
    _require_ldf_extension()
    from pydbc.ldf_cpp_importer import import_ldf_cpp

    tmp_ldf = tmp_path / LDF_FILE.name
    shutil.copy(LDF_FILE, tmp_ldf)
    session = import_ldf_cpp(tmp_ldf)

    networks = session.query(model.LinNetwork).all()
    assert len(networks) == 1
    signals = session.query(model.LinSignal).all()
    assert len(signals) > 0
    frames = session.query(model.LinUnconditionalFrame).all()
    assert len(frames) > 0
