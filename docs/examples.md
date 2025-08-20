# Examples

The following examples mirror and extend pydbc/examples/api_examples.py and demonstrate how to use the high‑level APIs.

Run examples interactively (Windows PowerShell):

```powershell
poetry run python -i pydbc\examples\api_examples.py
```

Or import and call the functions:

```python
from pydbc.examples.api_examples import dbc_example, ldf_example, ncf_example

dbc_example()
ldf_example()
ncf_example()
```

## DBC example (CAN)

```python
from pydbc.api.dbc import DBCCreator

dbc = DBCCreator(":memory:")
engine = dbc.create_node("Engine")
gateway = dbc.create_node("Gateway")
engine_data = dbc.create_message("EngineData", 100, 8, engine)

petrol_level = dbc.create_signal(
    "PetrolLevel", 8,
    byteorder=1, sign=1,
    formula_factor=1.0, formula_offset=0.0,
    minimum=0, maximum=255, unit="l",
)

vehicle_speed = dbc.create_signal(
    "VehicleSpeed", 16,
    byteorder=1, sign=1,
    formula_factor=0.1, formula_offset=0.0,
    minimum=0, maximum=300, unit="km/h",
)

dbc.add_signal_to_message(engine_data, petrol_level, 24)
dbc.add_signal_to_message(engine_data, vehicle_speed, 0)

# optional: receivers
# dbc.add_node_as_receiver(vehicle_speed, gateway)

dbc.commit()
dbc.close()
```

## LDF example (LIN)

```python
from pydbc.api.ldf import LDFCreator

ldf = LDFCreator(":memory:")
network = ldf.create_network("LINNetwork1", protocol_version="2.1", speed=19.2)
master = ldf.create_master_node("MasterECU", timebase=0.005, jitter=0.0001)
slave1 = ldf.create_slave_node("SlaveNode1", protocol_version="2.1", configured_NAD=1, initial_NAD=1)

motor_speed = ldf.create_signal("MotorSpeed", signal_size=16, init_value=0, publisher=master)
frame = ldf.create_unconditional_frame("MasterFrame", frame_id=0x10, size=2, publisher=master)
ldf.add_signal_to_frame(frame, motor_speed, 0)

ldf.commit()
ldf.close()
```

## NCF example (Vehicle config)

```python
from pydbc.api.ncf import NCFCreator

ncf = NCFCreator(":memory:")
vehicle = ncf.create_vehicle("TestVehicle")
can_network = ncf.create_network("CANNetwork", protocol="CAN", speed=500)
engine_ecu = ncf.create_ecu("EngineECU")
engine_node = ncf.create_node("EngineNode")

ncf.add_network_to_vehicle(vehicle, can_network)
ncf.add_ecu_to_vehicle(vehicle, engine_ecu)
ncf.add_node_to_network(can_network, engine_node)
ncf.add_node_to_ecu(engine_ecu, engine_node)

ncf.commit()
ncf.close()
```

## python-can integration example

```python
# Run the dedicated example script
# poetry run python pydbc\examples\python_can_examples.py
```

## Code generation examples

See pydbc/examples/generate_code_examples.py to generate:
- MicroPython CAN app (micropython_app.py)
- Linux SocketCAN C program (socketcan_app.c)

Run:
```powershell
poetry run python pydbc\examples\generate_code_examples.py
```

## Exporters

```python
from pydbc.db.imex import DbcExporter, LdfExporter

DbcExporter(":memory:").run()
LdfExporter(":memory:").run()
```

The exporters use templates in pydbc/cgen/templates and render a text file named testfile.txt.render.


## Import a .dbc and query messages

```python
from pydbc.api.imports import import_dbc
from pydbc.db.model import Message

# Parse the DBC file and get a SQLAlchemy session
session = import_dbc("C:\\path\\to\\file.dbc")

# Count all messages
print("Messages:", session.query(Message).count())

# List message names and IDs
for m in session.query(Message).order_by(Message.message_id).all():
    print(f"0x{m.message_id:X} {m.name}")
```

## Open an existing .vndb and query messages/signals

```python
from pydbc.api.imports import open_vndb
from pydbc.db.model import Message

vndb = open_vndb("C:\\path\\to\\database.vndb")
session = vndb.session

# Find one message and print its signals
msg = session.query(Message).filter_by(name="EngineData").first()
if msg:
    print("Message:", msg.name, hex(msg.message_id), "dlc=", msg.dlc)
    for ms in msg.signals:  # Message_Signal association
        s = ms.signal
        print(f"  {s.name}: start={ms.offset} size={s.bitsize} unit={s.unit}")
```
