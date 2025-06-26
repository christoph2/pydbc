#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Examples demonstrating the use of the pyDBC creational APIs.

This module contains examples for creating DBC, LDF, and NCF components
using the high-level APIs provided by pyDBC.
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


def dbc_example():
    """Example demonstrating the DBC API for CAN database creation."""
    from pydbc.api.dbc import DBCCreator
    
    print("Creating a CAN database using the DBC API...")
    
    # Create a new DBC creator with an in-memory database
    dbc = DBCCreator(":memory:")
    
    # Create nodes (ECUs)
    engine = dbc.create_node("Engine")
    gateway = dbc.create_node("Gateway")
    dashboard = dbc.create_node("Dashboard")
    dbc.session.commit()
    # Create messages
    engine_data = dbc.create_message("EngineData", 100, 8, engine)
    vehicle_status = dbc.create_message("VehicleStatus", 200, 8, gateway)

    dbc.session.commit()

    # Create signals
    petrol_level = dbc.create_signal(
        "PetrolLevel", 8, byteorder=1, sign=1,
        formula_factor=1.0, formula_offset=0.0,
        minimum=0, maximum=255, unit="l"
    )
    
    engine_power = dbc.create_signal(
        "EnginePower", 16, byteorder=1, sign=1,
        formula_factor=0.01, formula_offset=0.0,
        minimum=0, maximum=150, unit="kw"
    )
    
    engine_force = dbc.create_signal(
        "EngineForce", 16, byteorder=1, sign=1,
        formula_factor=1.0, formula_offset=0.0,
        minimum=0, maximum=0, unit="N"
    )
    
    vehicle_speed = dbc.create_signal(
        "VehicleSpeed", 16, byteorder=1, sign=1,
        formula_factor=0.1, formula_offset=0.0,
        minimum=0, maximum=300, unit="km/h"
    )
    dbc.session.commit()
    # Add signals to messages
    dbc.add_signal_to_message(engine_data, petrol_level, 24)
    dbc.add_signal_to_message(engine_data, engine_power, 48)
    dbc.add_signal_to_message(engine_data, engine_force, 32)
    dbc.add_signal_to_message(vehicle_status, vehicle_speed, 0)

    dbc.session.commit()

    # Add signal receivers
    # dbc.add_node_as_receiver(petrol_level, dashboard)
    # dbc.add_node_as_receiver(vehicle_speed, dashboard)

    dbc.session.commit()

    # Create a value table
    dbc.create_valuetable("EngineStatus", {
        0: "Running",
        1: "Idle",
        2: "Stopped"
    })
    
    # Commit changes to the database
    dbc.commit()
    
    # Query and print some information
    print(f"Created {len(dbc._nodes)} nodes: {', '.join(dbc._nodes.keys())}")
    print(f"Created {len(dbc._messages)} messages: {', '.join(dbc._messages.keys())}")
    print(f"Created {len(dbc._signals)} signals: {', '.join(dbc._signals.keys())}")
    
    # Close the database
    dbc.close()
    print("DBC example completed.\n")


def ldf_example():
    """Example demonstrating the LDF API for LIN network creation."""
    from pydbc.api.ldf import LDFCreator
    
    print("Creating a LIN network using the LDF API...")
    
    # Create a new LDF creator with an in-memory database
    ldf = LDFCreator(":memory:")
    
    # Create a LIN network
    network = ldf.create_network(
        "LINNetwork1",
        protocol_version="2.1",
        language_version="2.1",
        speed=19.2,
        channel_name="LIN1"
    )
    
    # Create master node
    master = ldf.create_master_node(
        "MasterECU",
        timebase=0.005,
        jitter=0.0001
    )
    
    # Create slave nodes
    slave1 = ldf.create_slave_node(
        "SlaveNode1",
        protocol_version="2.1",
        configured_NAD=1,
        initial_NAD=1,
        product_id=(0x1234, 0x5678, 0x01)
    )
    
    slave2 = ldf.create_slave_node(
        "SlaveNode2",
        protocol_version="2.1",
        configured_NAD=2,
        initial_NAD=2,
        product_id=(0x1234, 0x5679, 0x01)
    )
    
    # Create signals
    motor_speed = ldf.create_signal(
        "MotorSpeed",
        signal_size=16,
        init_value=0,
        publisher=master
    )
    
    motor_position = ldf.create_signal(
        "MotorPosition",
        signal_size=8,
        init_value=0,
        publisher=slave1
    )
    
    temperature = ldf.create_signal(
        "Temperature",
        signal_size=8,
        init_value=20,
        publisher=slave2
    )
    
    # Add signal subscribers
    ldf.add_signal_subscriber(motor_speed, slave1)
    ldf.add_signal_subscriber(motor_position, master)
    ldf.add_signal_subscriber(temperature, master)
    
    # Create frames
    master_frame = ldf.create_unconditional_frame(
        "MasterFrame",
        frame_id=0x10,
        size=2,
        publisher=master
    )
    
    slave1_frame = ldf.create_unconditional_frame(
        "Slave1Frame",
        frame_id=0x20,
        size=1,
        publisher=slave1
    )
    
    slave2_frame = ldf.create_unconditional_frame(
        "Slave2Frame",
        frame_id=0x30,
        size=1,
        publisher=slave2
    )
    
    # Add signals to frames
    ldf.add_signal_to_frame(master_frame, motor_speed, 0)
    ldf.add_signal_to_frame(slave1_frame, motor_position, 0)
    ldf.add_signal_to_frame(slave2_frame, temperature, 0)
    
    # Create a schedule table
    schedule_table = ldf.create_schedule_table("NormalTable")
    
    # Add frames to the schedule table
    ldf.add_frame_to_schedule_table(schedule_table, master_frame, 0.01)
    ldf.add_frame_to_schedule_table(schedule_table, slave1_frame, 0.02)
    ldf.add_frame_to_schedule_table(schedule_table, slave2_frame, 0.03)
    
    # Create signal encoding
    encoding = ldf.create_signal_encoding_type("TemperatureEncoding")
    
    # Add logical values to encoding
    ldf.add_logical_value_to_encoding(encoding, 0, "Error")
    ldf.add_logical_value_to_encoding(encoding, 255, "Not Available")
    
    # Add physical range to encoding
    ldf.add_physical_range_to_encoding(
        encoding,
        min_value=1,
        max_value=254,
        scale=0.5,
        offset=-40,
        text_info="Temperature in Celsius"
    )
    
    # Associate signal with encoding
    ldf.add_signal_representation(temperature, encoding)
    
    # Commit changes to the database
    ldf.commit()
    
    # Query and print some information
    print(f"Created {len(ldf._nodes)} nodes: {', '.join(ldf._nodes.keys())}")
    print(f"Created {len(ldf._frames)} frames: {', '.join(ldf._frames.keys())}")
    print(f"Created {len(ldf._signals)} signals: {', '.join(ldf._signals.keys())}")
    
    # Close the database
    ldf.close()
    print("LDF example completed.\n")


def ncf_example():
    """Example demonstrating the NCF API for network configuration creation."""
    from pydbc.api.ncf import NCFCreator
    
    print("Creating a network configuration using the NCF API...")
    
    # Create a new NCF creator with an in-memory database
    ncf = NCFCreator(":memory:")
    
    # Create a vehicle
    vehicle = ncf.create_vehicle("TestVehicle")
    
    # Create networks
    can_network = ncf.create_network("CANNetwork", protocol="CAN", speed=500)
    lin_network = ncf.create_network("LINNetwork", protocol="LIN", speed=19.2)
    
    # Create ECUs
    engine_ecu = ncf.create_ecu("EngineECU")
    body_ecu = ncf.create_ecu("BodyECU")
    gateway_ecu = ncf.create_ecu("GatewayECU")
    
    # Create nodes
    engine_node = ncf.create_node("EngineNode")
    body_node = ncf.create_node("BodyNode")
    gateway_can_node = ncf.create_node("GatewayCANNode")
    gateway_lin_node = ncf.create_node("GatewayLINNode")
    
    # Add networks to vehicle
    ncf.add_network_to_vehicle(vehicle, can_network)
    ncf.add_network_to_vehicle(vehicle, lin_network)
    
    # Add ECUs to vehicle
    ncf.add_ecu_to_vehicle(vehicle, engine_ecu)
    ncf.add_ecu_to_vehicle(vehicle, body_ecu)
    ncf.add_ecu_to_vehicle(vehicle, gateway_ecu)
    
    # Add nodes to networks
    ncf.add_node_to_network(can_network, engine_node)
    ncf.add_node_to_network(can_network, gateway_can_node)
    ncf.add_node_to_network(lin_network, body_node)
    ncf.add_node_to_network(lin_network, gateway_lin_node)
    
    # Add nodes to ECUs
    ncf.add_node_to_ecu(engine_ecu, engine_node)
    ncf.add_node_to_ecu(body_ecu, body_node)
    ncf.add_node_to_ecu(gateway_ecu, gateway_can_node)
    ncf.add_node_to_ecu(gateway_ecu, gateway_lin_node)
    
    # Create environment variables
    engine_temp = ncf.create_env_var(
        "EngineTemperature",
        var_type="INT",
        unit="°C",
        minimum=0,
        maximum=150,
        initial_value="90"
    )
    
    vehicle_speed = ncf.create_env_var(
        "VehicleSpeed",
        var_type="INT",
        unit="km/h",
        minimum=0,
        maximum=250,
        initial_value="0"
    )
    
    # Add environment variables to ECUs
    ncf.add_env_var_to_ecu(engine_ecu, engine_temp)
    ncf.add_env_var_to_ecu(gateway_ecu, vehicle_speed)
    
    # Add access nodes to environment variables
    ncf.add_access_node_to_env_var(engine_temp, engine_node, "write")
    ncf.add_access_node_to_env_var(engine_temp, gateway_can_node, "read")
    ncf.add_access_node_to_env_var(vehicle_speed, gateway_can_node, "write")
    ncf.add_access_node_to_env_var(vehicle_speed, gateway_lin_node, "read")
    
    # Create environment variable data
    ncf.create_env_var_data(engine_temp, "90")
    ncf.create_env_var_data(vehicle_speed, "0")
    
    # Commit changes to the database
    ncf.commit()
    
    # Query and print some information
    print(f"Created {len(ncf._vehicles)} vehicles: {', '.join(ncf._vehicles.keys())}")
    print(f"Created {len(ncf._networks)} networks: {', '.join(ncf._networks.keys())}")
    print(f"Created {len(ncf._ecus)} ECUs: {', '.join(ncf._ecus.keys())}")
    print(f"Created {len(ncf._nodes)} nodes: {', '.join(ncf._nodes.keys())}")
    
    # Close the database
    ncf.close()
    print("NCF example completed.\n")


if __name__ == "__main__":
    print("pyDBC API Examples\n" + "=" * 20 + "\n")
    
    # Run the examples
    dbc_example()
    # ldf_example()
    # ncf_example()
    
    print("All examples completed successfully.")