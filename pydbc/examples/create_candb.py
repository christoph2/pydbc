#!/usr/bin/env python
# -*- coding: utf-8 -*-

__copyright__ = """
   pySART - Simplified AUTOSAR-Toolkit for Python.

   (C) 2010-2020 by Christoph Schueler <cpu12.gems.googlemail.com>

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

import pydbc
from pydbc.types import BusType
import pydbc.db.model as model
from pydbc.db import CanDatabase

from sqlalchemy import event

@event.listens_for(model.Message.message_signals, 'append', retval = True)
def my_append_listener(target, value, initiator):
    print("target: {} \n\tvalue: {}\n".format(target, value, initiator))
    return value

#event.listen(model.Message.message_signals, 'append', my_append_listener)

DEBUG = False


def main():
    #cdb = CanDatabase.create("create_candb", debug = DEBUG)
    cdb = CanDatabase.create(":memory:", debug = DEBUG)
    #cdb = CanDatabase.open("create_candb", debug = DEBUG)
    session = cdb.session

    engine = model.Node(name = "Engine")
    gateway = model.Node(name = "Gateway")
    session.add_all([engine, gateway])


    engine_data = model.Message(name = "EngineData", message_id = 100, dlc = 8, sender = engine.rid)
    session.add(engine_data)

    petrolLevel = model.Signal(name = "PetrolLevel", bitsize = 8, byteorder = 1,
        sign = +1, formula_factor = 1.0, formula_offset = 0.0, minimum = 0, maximum = 255, unit = "l"
    )
    engPower = model.Signal(name = "EngPower", bitsize = 16, byteorder = 1,
        sign = +1, formula_factor = 0.01, formula_offset = 0.0, minimum = 0, maximum = 150, unit = "kw"
    )
    engForce = model.Signal(name = "EngForce", bitsize = 16, byteorder = 1,
        sign = +1, formula_factor = 1.0, formula_offset = 0.0, minimum = 0, maximum = 0, unit = "N"
    )
    session.add_all([petrolLevel, engPower, engForce])

    ms0 = model.Message_Signal(message = engine_data, signal = petrolLevel, offset = 24)
    ms1 = model.Message_Signal(message = engine_data, signal = engPower, offset = 48)
    ms2 = model.Message_Signal(message = engine_data, signal = engForce, offset = 32)

    #petrolLevel.receiver.append(gateway)
    session.add_all([ms0, ms1, ms2])

    v0 = model.Value_Description(value = 0, value_description = "Running")
    v1 = model.Value_Description(value = 1, value_description = "Idle")
    vtgIdleRunning = model.Valuetable(name = "vtgIdleRunning", values = [v0, v1])
    session.add_all([v0, v1, vtgIdleRunning])

    msgs = session.query(model.Message).all()
    for msg in msgs:
        print(msg.signals)

    session.flush()
    session.commit()

if __name__ == '__main__':
    main()

"""


"""
