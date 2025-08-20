# Tutorial

This tutorial walks you through creating a small but complete set of artifacts with pyDBC:
- A CAN database (DBC) with nodes, messages, and signals
- A LIN network (LDF) with master/slave nodes, frames, schedule tables
- A vehicle configuration (NCF) with vehicle, networks, ECUs, nodes, and environment variables

Where relevant, we also show how to export DBC/LDF using the provided exporters and how to parse existing DBC files.

Prerequisites:
- Python 3.10+
- Clone the repository and install dependencies (see docs/getting-started.md)

## 1. DBC: Build a small CAN database

```python
from pydbc.api.dbc import DBCCreator

# Create the in-memory database
dbc = DBCCreator(":memory:")

# Nodes
engine = dbc.create_node("Engine")
dashboard = dbc.create_node("Dashboard")

# Messages (sender can be Node object or its name)
engine_data = dbc.create_message("EngineData", message_id=0x64, dlc=8, sender=engine)

# Signals with scaling and units
rpm = dbc.create_signal(
    "EngineRPM", bitsize=16, byteorder=1, sign=1,
    formula_factor=0.25, formula_offset=0.0,
    minimum=0, maximum=8000, unit="rpm",
)

speed = dbc.create_signal(
    "VehicleSpeed", bitsize=16, byteorder=1, sign=1,
    formula_factor=0.1, formula_offset=0.0,
    minimum=0, maximum=300, unit="km/h",
)

# Map signals into the message payload
dbc.add_signal_to_message(engine_data, rpm, offset=0)
dbc.add_signal_to_message(engine_data, speed, offset=16)

# (optional) Receivers – declare which node subscribes to which signal
# dbc.add_node_as_receiver(speed, dashboard)

dbc.commit()
```

Tips:
- byteorder: 1 = little‑endian, 0 = big‑endian
- sign: 1 = unsigned, 0 = signed
- formula_factor and formula_offset define the physical conversion

## 2. LDF: Build a small LIN network

```python
from pydbc.api.ldf import LDFCreator

ldf = LDFCreator(":memory:")
network = ldf.create_network("LinDemo", protocol_version="2.1", language_version="2.1", speed=19.2)

# Nodes
master = ldf.create_master_node("MasterECU", timebase=0.005, jitter=0.0001)
slave1 = ldf.create_slave_node("Slave1", configured_NAD=1, initial_NAD=1, protocol_version="2.1")

# Signals (publisher can be name or node object)
temp = ldf.create_signal("Temperature", signal_size=8, init_value=20, publisher=slave1)

# Frame and mapping
frame = ldf.create_unconditional_frame("MasterFrame", frame_id=0x10, size=2, publisher=master)
ldf.add_signal_to_frame(frame, temp, signal_offset=0)

# Schedule table
sched = ldf.create_schedule_table("Normal")
ldf.add_frame_to_schedule_table(sched, frame, frame_time=0.01)

# Encoding for temperature
enc = ldf.create_signal_encoding_type("TemperatureEncoding")
ldf.add_logical_value_to_encoding(enc, 0, "Error")
ldf.add_logical_value_to_encoding(enc, 255, "N/A")
ldf.add_physical_range_to_encoding(enc, min_value=1, max_value=254, scale=0.5, offset=-40, text_info="°C")
ldf.add_signal_representation(temp, enc)

ldf.commit()
```

## 3. NCF: Build a small vehicle configuration

```python
from pydbc.api.ncf import NCFCreator

ncf = NCFCreator(":memory:")
vehicle = ncf.create_vehicle("DemoVehicle")
can_net = ncf.create_network("CAN1", protocol="CAN", speed=500)
lin_net = ncf.create_network("LIN1", protocol="LIN", speed=19.2)

engine_ecu = ncf.create_ecu("EngineECU")
body_ecu = ncf.create_ecu("BodyECU")

engine_node = ncf.create_node("EngineNode")
body_node = ncf.create_node("BodyNode")

# wire up the topology
ncf.add_network_to_vehicle(vehicle, can_net)
ncf.add_network_to_vehicle(vehicle, lin_net)

ncf.add_ecu_to_vehicle(vehicle, engine_ecu)
ncf.add_ecu_to_vehicle(vehicle, body_ecu)

ncf.add_node_to_network(can_net, engine_node)
ncf.add_node_to_network(lin_net, body_node)

ncf.add_node_to_ecu(engine_ecu, engine_node)
ncf.add_node_to_ecu(body_ecu, body_node)

# environment variables
coolant = ncf.create_env_var("CoolantTemp", var_type="INT", unit="°C", minimum=0, maximum=150, initial_value="90")
ncf.add_env_var_to_ecu(engine_ecu, coolant)

ncf.commit()
```

## 4. Export to DBC/LDF text

Use the exporters to render a template output of the current DB (for demo/testing):

```python
from pydbc.db.imex import DbcExporter, LdfExporter

# Export DBC
dbx = DbcExporter(":memory:")
dbx.run()  # writes testfile.txt.render next to your working dir

# Export LDF
ldfx = LdfExporter(":memory:")
ldfx.run()  # writes testfile.txt.render
```

Note: The exporters render using packaged templates under pydbc/cgen/templates. They are intended for demonstration/round‑trip tests.

## 5. Parse an existing DBC file

pyDBC also contains a grammar‑based parser using ANTLR4 and a dedicated DBC listener that populates the SQLAlchemy model.

```python
from pydbc.parser import ParserWrapper
from pydbc.dbcListener import DbcListener

# grammar name must match available generated classes (installed with the project)
# startSymbol is the entry rule of the grammar (e.g., "dbcfile")
wrapper = ParserWrapper(
    grammarName="dbc",          # loads pydbc.py3.dbcLexer / dbcParser
    startSymbol="dbcfile",      # entry rule
    listenerClass=DbcListener,   # populates VNDB
    debug=False,
)

# Parse a file (encoding auto‑detected) and get a SQLAlchemy session
session = wrapper.parseFromFile("path\\to\\your\\file.dbc")

# Or parse from a string
session = wrapper.parseFromString("VERSION \"1.0\"; ...", dbname="demo")

print("syntax errors:", wrapper.numberOfSyntaxErrors)
```

The parser wrapper uses pydbc.utils.detect_encoding to open files with the best matching character set.

## 6. Querying your data (SQLAlchemy session)

All creators and the parser provide access to the underlying SQLAlchemy session via .session. For example, using the DBC creator shown above:

```python
from pydbc.db.model import Message, Signal

# obtain the SQLAlchemy session (e.g., from a creator)
from pydbc.api.dbc import DBCCreator
session = DBCCreator(":memory:").session

# count messages
n = session.query(Message).count()
print("Messages:", n)

# join signals of a message
msg = session.query(Message).filter_by(name="EngineData").first()
for ms in msg.signals:  # Message_Signal association
    print(ms.signal.name, ms.offset)
```

## 7. Next steps

- Review the Examples (docs/examples.md) which mirror and extend pydbc/examples/api_examples.py
- Look through the API Reference (docs/api-reference.md) for details and parameter hints
- Check the repository’s tests and example database files in the root for inspiration (e.g., *.vndb)
