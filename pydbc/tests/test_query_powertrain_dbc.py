#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Real-world test for section "6. Querying your data (SQLAlchemy session)".

This test parses the bundled DBC file PowerTrain-2.dbc using the high-level
import function and performs a few SQLAlchemy queries to validate that the
import succeeded and relationships work as expected.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from pydbc.api.imports import import_dbc
from pydbc.db.model import Message


@pytest.mark.parametrize("dbc_relpath", [
    # Keep the file under version control to ensure reproducibility.
    Path("pydbc") / "examples" / "dbc-files" / "PowerTrain-2.dbc",
    Path("pydbc") / "examples" / "PowerTrain-2.dbc",  # fallback: alternate location
])
def test_querying_session_with_powertrain_dbc(dbc_relpath: Path, tmp_path: Path):
    # Resolve the DBC path relative to repository root
    repo_root = Path(__file__).resolve().parents[2]
    dbc_path = (repo_root / dbc_relpath)
    if not dbc_path.exists():
        pytest.skip(f"Sample DBC not found: {dbc_path}")

    # The ParserWrapper will create a VNDB file with the base name in the current
    # working directory. To avoid polluting the repo root, run from a temp dir.
    vndb_filename = "PowerTrain-2.vndb"

    # Change CWD to a temporary directory
    cwd_before = Path.cwd()
    try:
        # Switch to tmp to capture the generated VNDB here
        import os
        os.chdir(tmp_path)

        # Import the DBC and obtain a SQLAlchemy session
        session = import_dbc(str(dbc_path))

        # 1) Ensure we have messages
        total_msgs = session.query(Message).count()
        assert total_msgs > 0

        # 2) Find a well-known message present in this DBC
        msg = session.query(Message).filter_by(name="VECTOR__INDEPENDENT_SIG_MSG").first()
        assert msg is not None
        # In this file, the ID is 3221225472 and DLC is 0
        assert msg.message_id == 3221225472
        assert msg.dlc == 0

        # 3) Iterate signals via the association and check a known signal
        # msg.signals returns Message_Signal association rows
        tire_temp_assoc = None
        for ms in msg.signals:
            if ms.signal and ms.signal.name == "TireTemp":
                tire_temp_assoc = ms
                break
        assert tire_temp_assoc is not None, "Expected signal 'TireTemp' not found in VECTOR__INDEPENDENT_SIG_MSG"

        s = tire_temp_assoc.signal
        # From the DBC: 0|16@1+ (0.03125,-273) ... "deg"
        assert s.bitsize == 16
        assert s.unit == "deg"
        # The start bit (offset) should be 0 according to the message definition
        assert tire_temp_assoc.offset == 0

    finally:
        # Cleanup: close session/engine and remove generated VNDB if exists
        try:
            # Close underlying connection to release file lock on Windows
            if 'session' in locals():
                engine = session.get_bind() if hasattr(session, 'get_bind') else None
                session.close()
                if engine is not None:
                    engine.dispose()
        except Exception:
            pass

        try:
            vndb_path = tmp_path / vndb_filename
            if vndb_path.exists():
                vndb_path.unlink()
        except Exception:
            pass

        # Restore original working directory
        import os
        os.chdir(cwd_before)
