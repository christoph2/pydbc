# Code Generation (Mako)

This guide shows how to generate standalone applications from your pyDBC session using Mako templates.
The generated code embeds your CAN database (messages and signals); no runtime database is required.

Currently supported generators:
- MicroPython CAN application (Python script)
- Linux SocketCAN C program

## Prerequisites
- A pyDBC SQLAlchemy session containing your messages/signals (via DBCCreator or ParserWrapper).

## Usage

```python
from pathlib import Path
from pydbc.api.dbc import DBCCreator
from pydbc.cgen.generators import MicroPythonCanAppGenerator, SocketCanCGenerator

# Build a tiny in-memory session (or parse an existing DBC to get a session)
dbc = DBCCreator(":memory:")
node = dbc.create_node("Engine")
dbc.create_message("EngineData", message_id=0x100, dlc=8, sender=node)
dbc.commit()
session = dbc.session

mpy = MicroPythonCanAppGenerator(session)
py_code = mpy.render(app_name="mpy_app", only=["EngineData"])  # optional filter by message names
Path("micropython_app.py").write_text(py_code, encoding="utf-8")

sc = SocketCanCGenerator(session)
c_code = sc.render(program_name="socketcan_app", only=["EngineData"])  # optional filter
Path("socketcan_app.c").write_text(c_code, encoding="utf-8")
```

See a ready-to-run example at:
- pydbc/examples/generate_code_examples.py

## MicroPython CAN app
The generated micropython_app.py includes:
- Little-endian (Intel) bit packing/unpacking helpers
- Embedded message/signal metadata
- encode_message_by_name(name, values) -> (id, data, dlc)
- decode_message_by_id(id, data) -> {"message": name, "signals": {...}}
- A simple demo_send_once() that attempts to send one frame using machine.CAN or pyb.CAN

Note: You may need to adapt CAN initialization parameters (prescaler, timing) to your board.

## Linux SocketCAN C program
The generated socketcan_app.c includes:
- Little-endian bit packing/unpacking helpers
- Embedded message/signal metadata tables
- encode_message/decode_message functions using parallel double arrays
- A minimal main() that opens the given CAN interface, sends the first embedded message (zeroed values), and waits for a frame to decode

Build example:
```bash
gcc -O2 -Wall -o socketcan_app socketcan_app.c
sudo ./socketcan_app vcan0
```

To create a virtual CAN interface (Linux):
```bash
sudo modprobe vcan
sudo ip link add dev vcan0 type vcan
sudo ip link set up vcan0
```

## Limitations
- Signals assumed little-endian (Intel). Big-endian (Motorola) signals are not yet generated.
- Multiplexed signals are not yet handled specially.
- DLC up to 8 supported in the simple templates (CAN FD can be added later).

## Extending
The templates live under pydbc/cgen/templates. You can copy and customize them or contribute improvements:
- pydbc/cgen/templates/micropython_can.py.tmpl
- pydbc/cgen/templates/socketcan.c.tmpl

Rendering is done via pydbc.template.renderTemplateFromText, and templates are packaged via pkgutil.get_data.
