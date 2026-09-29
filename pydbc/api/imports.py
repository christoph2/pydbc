#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
High-level import helpers for existing network description files.

This module provides small wrapper functions around pydbc.parser.ParserWrapper
that import existing description files (.dbc, .ldf, .ncf) into a VNDB database
and return the SQLAlchemy session for further use. It also contains a helper to
open an existing .vndb database file.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional, Type

from pydbc.db import VNDB
from pydbc.dbcListener import DbcListener
from pydbc.utils import detect_encoding

from pydbc.dbc_cpp_importer import import_dbc_cpp  # type: ignore

try:
    from pydbc.ldfListener import LdfListener  # type: ignore
except Exception:  # optional depending on install
    LdfListener = None  # type: ignore
try:
    from pydbc.ldf_cpp_importer import import_ldf_cpp  # type: ignore
except Exception:
    import_ldf_cpp = None  # type: ignore
try:
    from pydbc.ncfListener import NcfListener  # type: ignore
except Exception:
    NcfListener = None  # type: ignore
try:
    from pydbc.ncf_cpp_importer import import_ncf_cpp  # type: ignore
except Exception:
    import_ncf_cpp = None  # type: ignore


def import_file(
    file_path: str | Path,
    *,
    grammar: str,
    start_symbol: str,
    listenerClass: Type,  # noqa: N803 (match existing style)
    encoding: Optional[str] = None,
    debug: bool = False,
    logLevel: str = "WARN",
) -> object:
    """Generic importer using a concrete grammar/listener.

    Returns the SQLAlchemy session created by VNDB. The resulting database
    is stored next to the input file using the same stem and the '.vndb' extension.
    """
    path = Path(file_path)
    if not path.exists() or not path.is_file():
        raise FileNotFoundError(f"Input file not found: {path}")

    enc = encoding or detect_encoding(str(path))

    try:
        from pydbc.parser import ParserWrapper
    except ImportError:
        raise RuntimeError(
            f"ANTLR parser not available (module 'pydbc.parser' not found). "
            f"Please use the C++ parser or ensure ANTLR components are generated."
        )

    parser = ParserWrapper(
        grammar,
        start_symbol,
        listenerClass,
        debug=debug,
        logLevel=logLevel,
        encoding=enc,
    )
    return parser.parseFromFile(str(path))


def import_dbc(
    file_path: str | Path,
    *,
    encoding: Optional[str] = None,
    debug: bool = False,
    logLevel: str = "WARN",
    as_vndb: bool = False,
    in_memory: bool = False,
) -> object | VNDB:
    """Import a .dbc file into a VNDB database and return the session or VNDB instance."""
    session = import_dbc_cpp(
        file_path, encoding=encoding, debug=debug, logLevel=logLevel, in_memory=in_memory
    )
    if as_vndb:
        return VNDB.from_session(session)
    return session

def import_ldf(
    file_path: str | Path,
    *,
    listenerClass: Optional[Type] = None,
    use_cpp: bool = True,
    encoding: Optional[str] = None,
    debug: bool = False,
    logLevel: str = "WARN",
    as_vndb: bool = False,
) -> object | VNDB:
    """Import a .ldf file into a VNDB database and return the session or VNDB instance."""
    if use_cpp and import_ldf_cpp is not None and listenerClass is None:
        session = import_ldf_cpp(
            file_path, encoding=encoding, debug=debug, logLevel=logLevel
        )
        if as_vndb:
            return VNDB.from_session(session)
        return session
    if listenerClass is None:
        if LdfListener is None:
            raise RuntimeError("LDF support not available: LdfListener not importable")
        listener = LdfListener
    else:
        listener = listenerClass
    session = import_file(
        file_path,
        grammar="ldf",
        start_symbol="lin_description_file",
        listenerClass=listener,
        encoding=encoding,
        debug=debug,
        logLevel=logLevel,
    )
    if as_vndb:
        return VNDB.from_session(session)
    return session


def import_ncf(
    file_path: str | Path,
    *,
    listenerClass: Optional[Type] = None,
    use_cpp: bool = True,
    encoding: Optional[str] = None,
    debug: bool = False,
    logLevel: str = "WARN",
    as_vndb: bool = False,
) -> object | VNDB:
    """Import a .ncf file into a VNDB database and return the session or VNDB instance."""
    if use_cpp and import_ncf_cpp is not None and listenerClass is None:
        session = import_ncf_cpp(
            file_path, encoding=encoding, debug=debug, logLevel=logLevel
        )
        if as_vndb:
            return VNDB.from_session(session)
        return session
    if listenerClass is None:
        if NcfListener is None:
            raise RuntimeError("NCF support not available: NcfListener not importable")
        listener = NcfListener
    else:
        listener = listenerClass
    session = import_file(
        file_path,
        grammar="ncf",
        start_symbol="toplevel",
        listenerClass=listener,
        encoding=encoding,
        debug=debug,
        logLevel=logLevel,
    )
    if as_vndb:
        return VNDB.from_session(session)
    return session


def open_vndb(
    file_path: str | Path, *, debug: bool = False, logLevel: str = "INFO"
) -> VNDB:
    """Open an existing .vndb database and return a VNDB instance.

    The returned object provides methods to query elements like
    networks, nodes, messages, and signals.
    """
    path = Path(file_path)
    if not path.exists() or not path.is_file():
        raise FileNotFoundError(f"VNDB file not found: {path}")
    # VNDB.open accepts a filename with or without extension; here we pass the path as-is
    return VNDB.open(str(path), debug=debug, logLevel=logLevel)


__all__ = [
    "import_file",
    "import_dbc",
    "import_ldf",
    "import_ncf",
    "open_vndb",
]
