pyDBC
=====

[![Build status](https://ci.appveyor.com/api/projects/status/6lf6kt2vle4jjou7?svg=true)](https://ci.appveyor.com/project/christoph2/pydbc)
[![Maintainability](https://api.codeclimate.com/v1/badges/ee1e493f62896f3fea61/maintainability)](https://codeclimate.com/github/christoph2/pydbc/maintainability)
[![Build Status](https://travis-ci.org/christoph2/pydbc.svg)](https://travis-ci.org/christoph2/pydbc)

[![GPL License](http://img.shields.io/badge/license-GPL-blue.svg)](http://opensource.org/licenses/GPL-2.0)

pyDBC is a library for creating and editing automotive network description files, including:
- DBC (CAN Database) files for CAN bus systems
- LDF (LIN Description File) for LIN networks
- NCF (Network Configuration File) for vehicle network configurations

---

## Installation

pyDBC is hosted on Github, get the latest release: [https://github.com/christoph2/pydbc](https://github.com/christoph2/pydbc)

### Using Poetry (recommended)

This project uses [Poetry](https://python-poetry.org/) for dependency management and packaging. If you don't have Poetry installed, you can install it by following the instructions on the [Poetry website](https://python-poetry.org/docs/#installation).

```bash
# Install the package
poetry install

# Run the tests
poetry run pytest
```

### Requirements

- Python >= 3.10
- SQLAlchemy >= 2.0.0
- Other dependencies are managed by Poetry

## First steps

pyDBC provides high-level creational APIs for working with automotive network description files. These APIs make it easy to create and manipulate DBC, LDF, and NCF components.

### Creating a CAN database (DBC)

```python
from pydbc.api.dbc import DBCCreator

# Create a new DBC creator with an in-memory database
dbc = DBCCreator(":memory:")

# Create nodes (ECUs)
engine = dbc.create_node("Engine")
gateway = dbc.create_node("Gateway")

# Create a message
engine_data = dbc.create_message("EngineData", 100, 8, engine)

# Create signals
petrol_level = dbc.create_signal(
    "PetrolLevel", 8, byteorder=1, sign=1,
    formula_factor=1.0, formula_offset=0.0,
    minimum=0, maximum=255, unit="l"
)

# Add signals to messages
dbc.add_signal_to_message(engine_data, petrol_level, 24)

# Add signal receivers
dbc.add_node_as_receiver(petrol_level, gateway)

# Commit changes to the database
dbc.commit()
```

### Creating a LIN network (LDF)

```python
from pydbc.api.ldf import LDFCreator

# Create a new LDF creator with an in-memory database
ldf = LDFCreator(":memory:")

# Create a LIN network
network = ldf.create_network(
    "LINNetwork1",
    protocol_version="2.1",
    speed=19.2
)

# Create master and slave nodes
master = ldf.create_master_node("MasterECU", timebase=0.005, jitter=0.0001)
slave = ldf.create_slave_node("SlaveNode1", configured_NAD=1)

# Create signals and frames
signal = ldf.create_signal("MotorSpeed", signal_size=16, init_value=0, publisher=master)
frame = ldf.create_unconditional_frame("MasterFrame", frame_id=0x10, size=2, publisher=master)

# Add signals to frames
ldf.add_signal_to_frame(frame, signal, 0)

# Commit changes to the database
ldf.commit()
```

### Creating a network configuration (NCF)

```python
from pydbc.api.ncf import NCFCreator

# Create a new NCF creator with an in-memory database
ncf = NCFCreator(":memory:")

# Create a vehicle
vehicle = ncf.create_vehicle("TestVehicle")

# Create networks and ECUs
can_network = ncf.create_network("CANNetwork", protocol="CAN", speed=500)
engine_ecu = ncf.create_ecu("EngineECU")

# Add networks to vehicle
ncf.add_network_to_vehicle(vehicle, can_network)

# Add ECUs to vehicle
ncf.add_ecu_to_vehicle(vehicle, engine_ecu)

# Commit changes to the database
ncf.commit()
```

For more detailed examples, see the `pydbc/examples/api_examples.py` file.

## Features

- High-level creational APIs for DBC, LDF, and NCF components
- SQLAlchemy-based database model for storing network configurations
- Support for all major components of automotive network description files
- Comprehensive examples demonstrating API usage

## License

GNU General Public License v2.0
