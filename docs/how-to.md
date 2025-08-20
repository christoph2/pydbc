# How‑to Guides

Task‑oriented guides that show how to accomplish common tasks with pyDBC.

## Parse a DBC file into the database and extend it

```python
from pydbc.parser import ParserWrapper
from pydbc.dbcListener import DbcListener
from pydbc.api.dbc import DBCCreator

wrapper = ParserWrapper(
    grammarName="dbc",
    startSymbol="dbcfile",
    listenerClass=DbcListener,
)

session = wrapper.parseFromFile("C:\\path\\to\\file.dbc")
print("syntax errors:", wrapper.numberOfSyntaxErrors)

# Attach creator to existing session to add/modify content
creator = DBCCreator.from_session(session)
creator.index_existing()  # optional
node = creator.create_node("AppNode")
msg = creator.create_message("AppMsg", message_id=0x321, dlc=8, sender=node)
sig = creator.create_signal("Counter", bitsize=8)
creator.add_signal_to_message(msg, sig, offset=0)
creator.commit()
```

Notes:
- File encoding is auto‑detected (pydbc.utils.detect_encoding); override by pre‑reading into a string and using parseFromString.
- The returned object is an SQLAlchemy session bound to the internal VNDB. You can attach DBCCreator to this session with DBCCreator.from_session.

## Export the current database as DBC/LDF text

```python
from pydbc.db.imex import DbcExporter, LdfExporter

DbcExporter(":memory:").run()  # produces testfile.txt.render
LdfExporter(":memory:").run()
```

To export a specific on‑disk VNDB instead of ":memory:", pass a Path to the .vndb file stem (see imex.Exporter for behavior), or adapt the exporter to your workflow.

## Create and link signals and messages (DBC)

```python
from pydbc.api.dbc import DBCCreator

dbc = DBCCreator(":memory:")
node = dbc.create_node("Sender")
msg = dbc.create_message("Msg", message_id=1, dlc=8, sender=node)
sig = dbc.create_signal("Sig", bitsize=8)
dbc.add_signal_to_message(msg, sig, offset=0)
dbc.commit()
```

## Add LIN subscribers to a signal (LDF)

```python
from pydbc.api.ldf import LDFCreator

ldf = LDFCreator(":memory:")
master = ldf.create_master_node("Master", timebase=0.005, jitter=0.0001)
slave = ldf.create_slave_node("Slave", configured_NAD=1)
sig = ldf.create_signal("Status", signal_size=8, init_value=0, publisher=master)
ldf.add_signal_subscriber(sig, slave)
ldf.commit()
```

## Add environment variables and access nodes (NCF)

```python
from pydbc.api.ncf import NCFCreator

ncf = NCFCreator(":memory:")
node = ncf.create_node("GatewayNode")
ecu = ncf.create_ecu("GatewayECU")
var = ncf.create_env_var("VehicleSpeed", var_type="INT", unit="km/h", minimum=0, maximum=250, initial_value="0")

ncf.add_env_var_to_ecu(ecu, var)
ncf.add_access_node_to_env_var(var, node, access_type="readWrite")
ncf.commit()
```

## Query data with SQLAlchemy

```python
from pydbc.db.model import Message, Signal
from pydbc.api.dbc import DBCCreator

session = DBCCreator(":memory:").session
print(session.query(Message).count())
```

## Use python-can to send/receive

See docs/python-can.md for a complete guide. Quick start:

```python
from pydbc.integrations.python_can import PythonCanSender, PythonCanReceiver, encode_message

# session: SQLAlchemy session after building/parsing your DBC
sender = PythonCanSender(bustype='virtual')
receiver = PythonCanReceiver(session, bustype='virtual')

arb_id, data, dlc = encode_message(session, 'YourMessage', {'YourSignal': 1.0})
sender.send(arb_id, data)
frame = receiver.recv(timeout=1.0)
```

## Troubleshooting

- If you encounter unexpected characters while parsing, verify the input encoding. You can pre‑open the file with the correct codec and call parseFromString.
- Multiplexing in DBC: use add_signal_to_message with multiplexor_signal/multiplex_dependent/multiplexor_value parameters when modeling multiplexed signals.
- Windows paths: In Python strings, escape backslashes (e.g., "C:\\Users\\...\\file.dbc").
