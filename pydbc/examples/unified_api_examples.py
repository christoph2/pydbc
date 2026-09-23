#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Examples for the unified pydbc.api interface."""

from __future__ import annotations


def can_to_unified_model_example() -> None:
    """Create a CAN database and adapt it to the unified NetworkDatabase model."""
    from pydbc.api import DBCCreator, as_network_database

    dbc = DBCCreator(":memory:")
    engine = dbc.create_node("Engine")
    gateway = dbc.create_node("Gateway")
    message = dbc.create_message("EngineData", 0x100, 8, engine)

    speed = dbc.create_signal(
        "VehicleSpeed",
        16,
        byteorder=1,
        sign=1,
        formula_factor=0.1,
        formula_offset=0.0,
        minimum=0,
        maximum=300,
        unit="km/h",
    )
    dbc.add_signal_to_message(message, speed, 0)
    dbc.add_node_as_receiver(speed, gateway)

    # Attributes (DBC ``BA_DEF_``/``BA_``) become plain dict entries on the
    # corresponding unified Node/Message/Signal objects.
    cycle_time_def = dbc.create_attribute_definition(
        "GenMsgCycleTime", "MESSAGE", "INT", minimum=0, maximum=10000
    )
    dbc.session.flush()
    dbc.set_attribute_value(cycle_time_def, message.rid, 100)
    dbc.commit()

    database = as_network_database(dbc.session, name="vehicle")
    print(f"nodes={len(database.nodes)} messages={len(database.messages)} signals={len(database.signals)}")
    print(database.messages[0].name, database.signals[0].name)
    print("message attributes:", database.messages[0].attributes)


def lin_to_unified_model_example() -> None:
    """Create a LIN database and adapt it to the unified NetworkDatabase model."""
    from pydbc.api import LDFCreator, as_network_database

    ldf = LDFCreator(":memory:")
    network = ldf.create_network("LINNetwork1", protocol_version="2.1", speed=19.2)
    master = ldf.create_master_node("MasterECU", timebase=0.005, jitter=0.0001)
    slave = ldf.create_slave_node("SlaveNode1", configured_NAD=1)
    signal = ldf.create_signal("MotorSpeed", signal_size=16, init_value=0, publisher=master)
    frame = ldf.create_unconditional_frame("MasterFrame", frame_id=0x10, size=2, publisher=master)
    ldf.add_signal_to_frame(frame, signal, 0)
    ldf.add_signal_subscriber(signal, slave)
    ldf.commit()

    database = as_network_database(ldf.session, name=network.name)
    print(f"bus_count={len(database.buses)} message_count={len(database.messages)} signal_count={len(database.signals)}")
    print(database.messages[0].name, database.signals[0].name)


def load_database_example(file_path: str) -> None:
    """Load a DBC or LDF file into the unified model."""
    from pydbc.api import load_database

    db = load_database(file_path)
    print(f"loaded {db.name} with {len(db.messages)} messages and {len(db.signals)} signals")


if __name__ == "__main__":
    can_to_unified_model_example()
    lin_to_unified_model_example()
