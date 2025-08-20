# Using pyDBC with python-can

This guide shows how to use a DBC you create (or parse) with pyDBC to send and receive
CAN frames via python-can.

Prerequisites:
- Python 3.10+
- pyDBC installed (this repository or from package)
- Optional: python-can installed for real sending/receiving

Installation (python-can):

```powershell
pip install python-can
```

On Windows you can use the built-in software-only "virtual" bus from python-can for experiments.

## 1) Create a simple DBC and encode a frame

```python
from pydbc.api.dbc import DBCCreator
from pydbc.integrations.python_can import encode_message, decode_message

# Build a tiny CAN database in memory
dbc = DBCCreator(":memory:")
engine = dbc.create_node("Engine")
msg = dbc.create_message("EngineData", message_id=0x100, dlc=8, sender=engine)

rpm = dbc.create_signal("EngineRPM", bitsize=16, byteorder=1, sign=1, formula_factor=0.25, formula_offset=0.0)
speed = dbc.create_signal("VehicleSpeed", bitsize=16, byteorder=1, sign=1, formula_factor=0.1, formula_offset=0.0)
temp = dbc.create_signal("CoolantTemp", bitsize=8, byteorder=1, sign=0, formula_factor=1.0, formula_offset=-40.0)

dbc.add_signal_to_message(msg, rpm, 0)
dbc.add_signal_to_message(msg, speed, 16)
dbc.add_signal_to_message(msg, temp, 32)

dbc.commit()
session = dbc.session

# Encode physical values -> CAN payload
can_id, data, dlc = encode_message(session, "EngineData", {
    "EngineRPM": 3000.0,
    "VehicleSpeed": 123.4,
    "CoolantTemp": 90.0,
})
print(f"Encoded: id=0x{can_id:X}, dlc={dlc}, data={data.hex()}")

# Decode back to physical values
decoded = decode_message(session, can_id, data)
print(decoded)
```

Notes:
- Currently, little-endian (Intel) signals are supported. Big-endian (Motorola) raises NotImplementedError.
- sign=1 is treated as unsigned, sign=0 as signed.
- Physical conversion: phys = raw * factor + offset.

## 2) Send/receive with python-can virtual bus

```python
from pydbc.integrations.python_can import PythonCanSender, PythonCanReceiver

sender = PythonCanSender(bustype='virtual')
receiver = PythonCanReceiver(session, bustype='virtual')

arb_id, data, dlc = encode_message(session, 'EngineData', {
    'EngineRPM': 2000.0,
    'VehicleSpeed': 50.0,
    'CoolantTemp': 85.0,
})

sender.send(arb_id, data)
frame = receiver.recv(timeout=1.0)
if frame is not None:
    print(receiver.decode_frame(frame))

sender.shutdown()
receiver.shutdown()
```

If python-can is not installed, PythonCanSender/Receiver will raise a RuntimeError with guidance.

## 3) Parse an existing DBC, extend it, then use python-can

If you have a DBC file, you can parse it with pyDBC, optionally create additional
messages/signals on top of the parsed database, and then use the same encoding/decoding APIs.

```python
from pydbc.parser import ParserWrapper
from pydbc.dbcListener import DbcListener
from pydbc.api.dbc import DBCCreator
from pydbc.integrations.python_can import encode_message, decode_message

# Parse the DBC into the internal database and get a SQLAlchemy session
wrapper = ParserWrapper(
    grammarName='dbc', startSymbol='dbcfile', listenerClass=DbcListener
)
session = wrapper.parseFromFile('C:\\path\\to\\file.dbc')

# Attach a creator to the existing session to add new content
creator = DBCCreator.from_session(session)
creator.index_existing()  # optional: preload existing items for convenience

# Example: add a new message and signal next to the parsed ones
node = creator.create_node('MyNewNode')
msg = creator.create_message('AppStatus', message_id=0x555, dlc=8, sender=node)
sig = creator.create_signal('AliveCounter', bitsize=4, byteorder=1, sign=1)
creator.add_signal_to_message(msg, sig, offset=0)
creator.commit()

# Now encode a frame using either parsed or newly created messages
can_id, data, dlc = encode_message(session, 'AppStatus', {'AliveCounter': 7})
```

## 4) Example script

A ready-to-run example is provided:
- pydbc/examples/python_can_examples.py

Run encode/decode cycle without bus:

```powershell
poetry run python pydbc\examples\python_can_examples.py
```entries

Try the virtual bus demo by uncommenting the call in that script and ensuring python-can is installed.

## 5) Limitations and next steps

- Only little-endian signals are supported at the moment. Support for big-endian (Motorola) bit packing can be added next.
- Multiplexed signals are not handled specifically here; if present in the DB, the current simple encoder will just place bits. For complex multiplexing behavior, extend the adapter to respect multiplexor rules.
- This module intentionally keeps python-can as an optional dependency.
