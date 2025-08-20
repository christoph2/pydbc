# Getting Started

This guide helps you install pyDBC and create your first network database using its high‑level creational APIs.

## Installation

pyDBC uses Poetry for development and dependency management. You can also install it into an existing environment.

- Python: 3.10+
- SQLAlchemy: 2.0+

Using Poetry in a clone of the repository:

```powershell
# from the project root
poetry install

# run tests (if any)
poetry run pytest
```

Using pip directly (when published):

```powershell
pip install pydbc
```

## Quickstart: Create a CAN DBC in memory

```python
from pydbc.api.dbc import DBCCreator

# create an in‑memory DB
dbc = DBCCreator(":memory:")

# nodes (ECUs)
engine = dbc.create_node("Engine")
gateway = dbc.create_node("Gateway")

# message
engine_data = dbc.create_message("EngineData", message_id=100, dlc=8, sender=engine)

# signals
petrol_level = dbc.create_signal(
    "PetrolLevel", bitsize=8,
    byteorder=1, sign=1,
    formula_factor=1.0, formula_offset=0.0,
    minimum=0, maximum=255, unit="l",
)

# assign signal to message at bit offset 24
dbc.add_signal_to_message(engine_data, petrol_level, offset=24)

# commit to persist
dbc.commit()
```

## Quickstart: Create a LIN network (LDF)

```python
from pydbc.api.ldf import LDFCreator

ldf = LDFCreator(":memory:")
network = ldf.create_network("LINNetwork1", protocol_version="2.1", speed=19.2)
master = ldf.create_master_node("MasterECU", timebase=0.005, jitter=0.0001)
signal = ldf.create_signal("MotorSpeed", signal_size=16, init_value=0, publisher=master)
frame = ldf.create_unconditional_frame("MasterFrame", frame_id=0x10, size=2, publisher=master)
ldf.add_signal_to_frame(frame, signal, signal_offset=0)
ldf.commit()
```

## Quickstart: Create a vehicle configuration (NCF)

```python
from pydbc.api.ncf import NCFCreator

ncf = NCFCreator(":memory:")
vehicle = ncf.create_vehicle("TestVehicle")
can_network = ncf.create_network("CANNetwork", protocol="CAN", speed=500)
engine_ecu = ncf.create_ecu("EngineECU")

ncf.add_network_to_vehicle(vehicle, can_network)
ncf.add_ecu_to_vehicle(vehicle, engine_ecu)

ncf.commit()
```

## Where to go next

- Tutorial: docs/tutorial.md — Build a small but complete model step‑by‑step.
- How‑to Guides: docs/how-to.md — Task‑oriented recipes (import/export, parsing, querying).
- API Reference: docs/api-reference.md — Classes and methods.
