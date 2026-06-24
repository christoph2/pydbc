#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Vehicle Network Database Importer

This script imports vehicle network description files (.dbc, .ldf, .ncf) into a database.
It creates a .vndb file for each input file.
"""

__copyright__ = """
   pySART - Simplified AUTOSAR-Toolkit for Python.

   (C) 2010-2023 by Christoph Schueler <cpu12.gems.googlemail.com>

   All Rights Reserved

   This program is free software; you can redistribute it and/or modify
   it under the terms of the GNU General Public License as published by
   the Free Software Foundation; either version 2 of the License, or
   (at your option) any later version.

   This program is distributed in the hope that it will be useful,
   but WITHOUT ANY WARRANTY; without even the implied warranty of
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
   GNU General Public License for more details.

   You should have received a copy of the GNU General Public License along
   with this program; if not, write to the Free Software Foundation, Inc.,
   51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

   s. FLOSS-EXCEPTION.txt
"""
__author__ = "Christoph Schueler"
__version__ = "0.1.0"

import argparse
import logging
import os
import pathlib
from typing import Optional, Union

from pydbc.db.model import Message, Network, Node, Signal
from pydbc.api.imports import import_dbc, import_ldf, import_ncf
from pydbc.types import FileType


def parseFile(
    pth: pathlib.Path,
    filetype: FileType,
    debug: bool = False,
    remove_file: bool = False,
    logLevel: str = "WARN",
) -> Optional[object]:
    """Parse a vehicle network description file and create a database.

    Args:
        pth: Path to the file to parse
        filetype: Type of the file (DBC, LDF, NCF)
        debug: Enable debug output
        remove_file: Remove existing database file before parsing
        logLevel: Logging level (WARN, INFO, ERROR, DEBUG)

    Returns:
        SQLAlchemy session object or None if parsing failed
    """
    logging.info(f"Processing '{pth}'")

    dbfn = pth.with_suffix(".vndb")
    if remove_file and dbfn.exists():
        try:
            dbfn.unlink()
        except PermissionError as e:
            logging.error(f"Permission error removing {dbfn}: {e}")
            return None
        except Exception as e:
            logging.error(f"Error removing {dbfn}: {e}")
            return None

    try:
        if filetype == FileType.DBC:
            session = import_dbc(pth, debug=debug, logLevel=logLevel.upper())
        elif filetype == FileType.LDF:
            session = import_ldf(pth, debug=debug, logLevel=logLevel.upper())
        elif filetype == FileType.NCF:
            session = import_ncf(pth, debug=debug, logLevel=logLevel.upper())
        else:
            raise ValueError(f"Invalid filetype '{filetype}'")

        logging.info(f"Successfully parsed {pth}")
        return session
    except Exception as e:
        logging.error(f"Error parsing {pth}: {e}")
        return None


def get_file_type(pth: pathlib.Path) -> Optional[FileType]:
    """Determine the file type based on the file extension.

    Args:
        pth: Path to the file

    Returns:
        FileType enum value or None if the file type is not supported
    """
    suffix = pth.suffix.lower()
    if suffix == ".dbc":
        result = FileType.DBC
    elif suffix == ".ldf":
        result = FileType.LDF
    elif suffix == ".ncf":
        result = FileType.NCF
    else:
        result = None
    return result


def importFile(pth: pathlib.Path, logLevel: str) -> Optional[object]:
    """Import a vehicle network description file into a database.

    Args:
        pth: Path to the file to import
        logLevel: Logging level (WARN, INFO, ERROR, DEBUG)

    Returns:
        SQLAlchemy session object or None if import failed
    """
    file_type = get_file_type(pth)
    if file_type is None:
        logging.error(f"Unsupported file type: {pth.suffix}")
        return None

    return parseFile(pth, file_type, remove_file=True, logLevel=logLevel)


def get_import_summary(session: object) -> dict[str, int]:
    """Collect summary counters of imported key entities."""
    return {
        "networks": session.query(Network).count(),
        "nodes": session.query(Node).count(),
        "messages": session.query(Message).count(),
        "signals": session.query(Signal).count(),
    }


def main() -> None:
    """Main entry point for the vndb_importer script."""
    footer = (
        "CAVEAT: In this version vndb_importer is DESTRUCTIVE, i.e. no merging happens!"
    )
    parser = argparse.ArgumentParser(
        description="Import vehicle network description files into a database.",
        epilog=footer,
    )
    parser.add_argument(
        "vehicle_file",
        help=".dbc, .ldf, or .ncf file(s) to import (glob patterns supported)",
        nargs="+",
    )
    parser.add_argument(
        "-k",
        dest="keepDirectory",
        action="store_true",
        default=False,
        help="keep directory; otherwise create db in current directory",
    )
    parser.add_argument(
        "-l",
        dest="loglevel",
        type=str,
        choices=["debug", "info", "warn", "error"],
        default="warn",
        help="logging level [debug | info | warn | error]",
    )
    parser.add_argument(
        "-w",
        dest="winout",
        action="store_true",
        help="Format output for Windows console.",
    )
    parser.add_argument(
        "-u",
        dest="ucout",
        action="store_true",
        help="Generate UTF-8 encoded output (otherwise Latin-1).",
    )

    args = parser.parse_args()

    # Configure logging
    log_level = getattr(logging, args.loglevel.upper())
    logging.basicConfig(level=log_level, format="%(levelname)s: %(message)s")

    # Process each input file
    stats = {
        "total": len(args.vehicle_file),
        "success": 0,
        "failed": 0,
        "missing": 0,
        "not_files": 0,
        "unsupported": 0,
        "networks": 0,
        "nodes": 0,
        "messages": 0,
        "signals": 0,
    }

    for arg in args.vehicle_file:
        # print(arg)
        pth = pathlib.Path(arg)
        if not pth.exists():
            logging.error(f"File not found: {pth}")
            stats["failed"] += 1
            stats["missing"] += 1
            continue

        if not pth.is_file():
            logging.error(f"Not a file: {pth}")
            stats["failed"] += 1
            stats["not_files"] += 1
            continue

        if get_file_type(pth) is None:
            logging.error(f"Unsupported file type: {pth.suffix} ({pth})")
            stats["failed"] += 1
            stats["unsupported"] += 1
            continue

        # Import the file
        session = importFile(pth, args.loglevel)
        if session:
            stats["success"] += 1
            summary = get_import_summary(session)
            stats["networks"] += summary["networks"]
            stats["nodes"] += summary["nodes"]
            stats["messages"] += summary["messages"]
            stats["signals"] += summary["signals"]
            logging.info(f"Successfully imported {pth}")
            logging.info(
                "Import summary for %s: networks=%d, nodes=%d, messages=%d, signals=%d",
                pth,
                summary["networks"],
                summary["nodes"],
                summary["messages"],
                summary["signals"],
            )
        else:
            stats["failed"] += 1
            logging.error(f"Failed to import {pth}")

    logging.warning(
        "Run summary: total=%d, successful=%d, failed=%d (missing=%d, not_file=%d, unsupported=%d) | imported: networks=%d, nodes=%d, messages=%d, signals=%d",
        stats["total"],
        stats["success"],
        stats["failed"],
        stats["missing"],
        stats["not_files"],
        stats["unsupported"],
        stats["networks"],
        stats["nodes"],
        stats["messages"],
        stats["signals"],
    )


if __name__ == "__main__":
    main()
