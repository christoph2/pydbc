# API Reference

This reference summarizes the main public classes and methods of pyDBC. For detailed parameter semantics, inspect the docstrings in the source files under pydbc/api and pydbc/db.

- DBC (CAN) Creator: pydbc.api.dbc.DBCCreator
- LDF (LIN) Creator: pydbc.api.ldf.LDFCreator
- NCF (Vehicle/Network Config) Creator: pydbc.api.ncf.NCFCreator
- Parser Wrapper: pydbc.parser.ParserWrapper
- Exporters: pydbc.db.imex.DbcExporter, pydbc.db.imex.LdfExporter

## pydbc.api.dbc — DBCCreator

Primary methods:
- DBCCreator(db_path=":memory:", debug=False, session=None)
- DBCCreator.from_session(session) -> DBCCreator
- index_existing() -> None  (preload caches from current session)
- create_network(name, **kwargs) -> Network
- create_node(name, **kwargs) -> Node
- create_message(name, message_id, dlc, sender, **kwargs) -> Message
- create_signal(name, bitsize, byteorder=1, sign=1, formula_factor=1.0, formula_offset=0.0, minimum=0.0, maximum=0.0, unit="", **kwargs) -> Signal
- add_signal_to_message(message, signal, offset, multiplexor_signal=None, multiplex_dependent=None, multiplexor_value=None) -> Message_Signal
- create_valuetable(name, values: dict[int, str]) -> Valuetable
- add_node_as_receiver(signal, node) -> Node_RxSignal
- create_attribute_definition(name, object_type, value_type, **kwargs) -> Attribute_Definition
- set_attribute_value(attribute_definition, object_id, value) -> Attribute_Value
- commit() -> None
- close() -> None

Notes:
- You can attach to a parsed database by passing session=... or using DBCCreator.from_session.
- sender can be a Node object, a node name string, or an integer rid.
- Name-based parameters are lazily resolved against the attached session if not found in local caches.
- add_signal_to_message offset is in bits.

## pydbc.api.ldf — LDFCreator

Primary methods:
- LDFCreator(db_path=":memory:", debug=False)
- create_network(name, protocol_version=None, language_version=None, speed=None, file_revision=None, channel_name=None, **kwargs) -> LinNetwork
- create_master_node(name, timebase, jitter, bit_length=None, tolerant=None, **kwargs) -> LinMasterNode
- create_slave_node(name, protocol_version=None, configured_NAD=None, initial_NAD=None, product_id=(), p2_min=None, st_min=None, n_as_timeout=None, n_cr_timeout=None, response_tolerance=None, **kwargs) -> LinSlaveNode
- create_signal(name, signal_size, init_value, publisher, **kwargs) -> LinSignal
- add_signal_subscriber(signal, subscriber) -> LinSignalSubscriber
- create_unconditional_frame(name, frame_id, size, publisher, **kwargs) -> LinUnconditionalFrame
- add_signal_to_frame(frame, signal, signal_offset=0) -> LinUnconditionalFrameSignal
- create_event_triggered_frame(name, frame_id, master_node, collision_resolving_schedule_table=None, **kwargs) -> LinEventTriggeredFrame
- create_sporadic_frame(name, **kwargs) -> LinSporadicFrame
- create_schedule_table(name, **kwargs) -> LinScheduleTable
- add_frame_to_schedule_table(schedule_table, frame, frame_time) -> LinScheduleTable_Command_Frame
- create_signal_encoding_type(name, **kwargs) -> LinSignalEncodingType
- add_logical_value_to_encoding(encoding_type, signal_value, text_info) -> LinSignalEncodingEntry_Logical
- add_physical_range_to_encoding(encoding_type, min_value, max_value, scale, offset, text_info) -> LinSignalEncodingEntry_Physical
- add_signal_representation(signal, encoding_type) -> LinSignalRepresentation
- commit() -> None
- close() -> None

Notes:
- publisher/subscriber parameters can be a name string or the corresponding node object.
- frame.size is in bytes; signal_offset is in bits.

## pydbc.api.ncf — NCFCreator

Primary methods:
- NCFCreator(db_path=":memory:", debug=False)
- create_network(name, **kwargs) -> Network
- create_node(name, **kwargs) -> Node
- create_ecu(name, **kwargs) -> ECU
- create_vehicle(name, **kwargs) -> Vehicle
- create_env_var(name, var_type, unit=None, minimum=None, maximum=None, initial_value=None, access_type=None, access_node=None, **kwargs) -> EnvVar
- create_gateway_signal(source_signal, target_signal, **kwargs) -> Gateway_Signal
- add_node_to_network(network, node, connector_name=None) -> Network_Node
- add_ecu_to_vehicle(vehicle, ecu) -> Vehicle_ECU
- add_network_to_vehicle(vehicle, network) -> Vehicle_Network
- add_node_to_ecu(ecu, node) -> ECU_Node
- add_env_var_to_ecu(ecu, env_var) -> ECU_EnvVar
- add_access_node_to_env_var(env_var, node, access_type) -> EnvVar_AccessNode
- create_env_var_data(env_var, data) -> EnvironmentVariablesData
- commit() -> None
- close() -> None

Notes:
- Many parameters accept either names or objects. Ensure referenced objects exist if passing names.

## pydbc.parser — ParserWrapper

Primary methods/properties:
- ParserWrapper(grammarName, startSymbol, listenerClass, debug=False, logLevel="INFO")
- parse(input, trace=False) -> Session
- parseFromFile(filename, encoding="ISO-8859-1", trace=False) -> Session
- parseFromString(buf, encoding="ISO-8859-1", trace=False, dbname=":memory:") -> Session
- stringStream(fname, encoding="ISO-8859-1") -> InputStream
- numberOfSyntaxErrors (property)

Notes:
- grammarName is used to dynamically import generated ANTLR lexer/parser classes (e.g., "dbc" -> pydbc.py3.dbcLexer/dbcParser).
- listenerClass should be a subclass of parser.BaseListener that populates the VNDB (e.g., DbcListener).

## pydbc.db.imex — Exporters

Classes:
- DbcExporter
- LdfExporter

Usage:
```python
from pydbc.db.imex import DbcExporter, LdfExporter
DbcExporter(":memory:").run()
LdfExporter(":memory:").run()
```

## Code generation (Mako)

Generators in pydbc.cgen.generators:
- MicroPythonCanAppGenerator(session)
  - render(only: list[str] | None = None, app_name: str = "pydbc_mpy_app") -> str
- SocketCanCGenerator(session)
  - render(only: list[str] | None = None, program_name: str = "pydbc_socketcan_app") -> str

Notes:
- The templates are embedded resources under pydbc/cgen/templates.
- Both outputs include little-endian bit packing/unpacking helpers and embedded message metadata.

See docs/code-generation.md for a full guide.

## python-can integration helpers

Module: pydbc.integrations.python_can

- encode_message(session, message_name, signal_values: dict[str, float]) -> tuple[int, bytes, int]
  - Returns (arbitration_id, data, dlc)
- decode_message(session, can_id: int, data: bytes) -> dict
  - Returns {"message": name, "signals": {sig: value}}
- PythonCanSender(**bus_kwargs)
  - send(arbitration_id: int, data: bytes, is_extended_id: bool = False)
  - shutdown()
- PythonCanReceiver(session, **bus_kwargs)
  - recv(timeout: float | None)
  - decode_frame(frame) -> dict
  - shutdown()

Notes:
- Little-endian signals supported. Big-endian not yet implemented.
- python-can is optional and imported lazily.

## Data model (ORM)

The SQLAlchemy ORM classes live in pydbc.db.model and include entities such as:
- Network, Node, Message, Signal, Message_Signal
- Valuetable, Value_Description, Attribute_Definition, Attribute_Value
- LIN‑specific: LinNetwork, LinNode, LinMasterNode, LinSlaveNode, LinSignal, LinUnconditionalFrame, LinScheduleTable, encoding types, etc.
- NCF/vehicle config entities: Vehicle, ECU, relations between vehicles, networks, nodes, ECUs, and environment variables.

Refer to the source for complete field lists and relationships.
