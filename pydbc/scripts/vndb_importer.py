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
__author__ = 'Christoph Schueler'
__version__ = '0.1.0'

import argparse
import logging
import os
import pathlib
from typing import Optional, Union

from pydbc.parser import ParserWrapper
from pydbc.dbcListener import DbcListener
from pydbc.ldfListener import LdfListener
from pydbc.ncfListener import NcfListener
from pydbc.types import FileType


def parseFile(pth: pathlib.Path, filetype: FileType, debug: bool = False, 
           remove_file: bool = False, logLevel: str = "WARN") -> Optional[object]:
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
    if filetype == FileType.DBC:
        grammar = 'dbc'
        start_symbol = 'dbcfile'
        listenerClass = DbcListener
    elif filetype == FileType.LDF:
        grammar = 'ldf'
        start_symbol = 'lin_description_file'
        listenerClass = LdfListener
    elif filetype == FileType.NCF:
        grammar = 'ncf'
        start_symbol = 'toplevel'
        listenerClass = NcfListener
    else:
        raise ValueError(f"Invalid filetype '{filetype}'")

    parser = ParserWrapper(grammar, start_symbol, listenerClass, debug=debug, logLevel=logLevel)
    logging.info(f"Processing '{pth}'")

    dbfn = f"{pth.stem}.vndb"
    if remove_file:
        try:
            os.unlink(dbfn)
        except FileNotFoundError:
            # File doesn't exist, no need to remove
            pass
        except PermissionError as e:
            logging.error(f"Permission error removing {dbfn}: {e}")
            return None
        except Exception as e:
            logging.error(f"Error removing {dbfn}: {e}")
            return None

    try:
        session = parser.parseFromFile(str(pth))
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
    if suffix == '.dbc':
        result = FileType.DBC
    elif suffix == '.ldf':
        result = FileType.LDF
    elif suffix == '.ncf':
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


def main() -> None:
    """Main entry point for the vndb_importer script."""
    footer = "CAVEAT: In this version vndb_importer is DESTRUCTIVE, i.e. no merging happens!"
    parser = argparse.ArgumentParser(
        description='Import vehicle network description files into a database.',
        epilog=footer
    )
    parser.add_argument(
        "vehicle_file",
        help=".dbc, .ldf, or .ncf file(s) to import (glob patterns supported)",
        nargs="+"
    )
    parser.add_argument(
        "-k",
        dest='keepDirectory',
        action="store_true",
        default=False,
        help="keep directory; otherwise create db in current directory"
    )
    parser.add_argument(
        "-l",
        dest="loglevel",
        type=str,
        choices=["debug", "info", "warn", "error"],
        default="warn",
        help="logging level [debug | info | warn | error]"
    )
    parser.add_argument(
        "-w",
        dest="winout",
        action="store_true",
        help="Format output for Windows console."
    )
    parser.add_argument(
        "-u",
        dest="ucout",
        action="store_true",
        help="Generate UTF-8 encoded output (otherwise Latin-1)."
    )

    args = parser.parse_args()

    # Configure logging
    log_level = getattr(logging, args.loglevel.upper())
    logging.basicConfig(
        level=log_level,
        format='%(levelname)s: %(message)s'
    )

    # Process each input file
    for arg in args.vehicle_file:
        for pth in pathlib.Path().glob(arg):
            if not pth.exists():
                logging.error(f"File not found: {pth}")
                continue

            if not pth.is_file():
                logging.error(f"Not a file: {pth}")
                continue

            # Import the file
            session = importFile(pth, args.loglevel)
            if session:
                logging.info(f"Successfully imported {pth}")
            else:
                logging.error(f"Failed to import {pth}")

if __name__ == '__main__':
    main()
