import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from pydbc.db.model import Base, Message, Signal, Message_Signal
from pydbc.types import ByteOrderType
from pydbc.cgen.generators import (
    PythonCanAppGenerator,
    MicroPythonCanAppGenerator,
    SocketCanCGenerator,
)
from pydbc.cgen.dsl_prototype import DBC_DSL, ByteOrder, to_cg_model
from pydbc.integrations.python_can import encode_message, decode_message


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    # Create Message
    msg = Message(name="MotorolaIntelMsg", message_id=0x123, dlc=8, type="Message")
    session.add(msg)
    session.flush()

    # 1. Little-endian unsigned signal: start_bit=0, size=16, factor=1.0, offset=0.0
    sig_le = Signal(
        name="Speed_LE",
        bitsize=16,
        byteorder=ByteOrderType.INTEL,  # 1
        sign=1,  # unsigned
        formula_factor=1.0,
        formula_offset=0.0,
        minimum=0.0,
        maximum=65535.0,
        type="Signal",
    )
    session.add(sig_le)
    session.flush()

    ms_le = Message_Signal(signal=sig_le, message=msg, offset=0)
    session.add(ms_le)

    # 2. Big-endian (Motorola) unsigned signal: start_bit=23 (Byte 2 bit 7), size=16, factor=0.5, offset=10.0
    # Bytes 2 and 3
    sig_be = Signal(
        name="RPM_BE",
        bitsize=16,
        byteorder=ByteOrderType.MOTOROLA,  # 0
        sign=1,  # unsigned
        formula_factor=0.5,
        formula_offset=10.0,
        minimum=10.0,
        maximum=32777.5,
        type="Signal",
    )
    session.add(sig_be)
    session.flush()

    ms_be = Message_Signal(signal=sig_be, message=msg, offset=23)
    session.add(ms_be)

    # 3. Big-endian (Motorola) signed signal: start_bit=39 (Byte 4 bit 7), size=12, factor=1.0, offset=0.0
    # Spans Byte 4 (bits 7..0, 8 bits) and Byte 5 (bits 7..4, 4 bits)
    sig_be_signed = Signal(
        name="Temp_BE_Signed",
        bitsize=12,
        byteorder=ByteOrderType.MOTOROLA,  # 0
        sign=0,  # signed
        formula_factor=1.0,
        formula_offset=0.0,
        minimum=-2048.0,
        maximum=2047.0,
        type="Signal",
    )
    session.add(sig_be_signed)
    session.flush()

    ms_be_signed = Message_Signal(signal=sig_be_signed, message=msg, offset=39)
    session.add(ms_be_signed)

    # 4. Big-endian (Motorola) unaligned signal: start_bit=43 (Byte 5 bit 3), size=10, factor=1.0, offset=0.0
    # Spans Byte 5 (bits 3..0, 4 bits) and Byte 6 (bits 7..2, 6 bits)
    sig_be_unaligned = Signal(
        name="Unaligned_BE",
        bitsize=10,
        byteorder=ByteOrderType.MOTOROLA,  # 0
        sign=1,  # unsigned
        formula_factor=1.0,
        formula_offset=0.0,
        minimum=0.0,
        maximum=1023.0,
        type="Signal",
    )
    session.add(sig_be_unaligned)
    session.flush()

    ms_be_unaligned = Message_Signal(signal=sig_be_unaligned, message=msg, offset=43)
    session.add(ms_be_unaligned)

    session.commit()
    yield session
    session.close()


def test_python_can_generator_byteorder(db_session):
    gen = PythonCanAppGenerator(db_session)
    code = gen.render(app_name="test_app")
    
    # Execute the generated code
    namespace = {}
    exec(code, namespace)
    
    encode_func = namespace["encode_message_by_name"]
    decode_func = namespace["decode_message_by_id"]
    
    # Values to encode
    values = {
        "Speed_LE": 1000.0,
        "RPM_BE": 510.0,  # raw = (510 - 10) / 0.5 = 1000 = 0x03E8
        "Temp_BE_Signed": -25.0,  # raw = -25 = 0xFFE7 & 0xFFF = 0xFE7
        "Unaligned_BE": 300.0,  # raw = 300 = 0x12C
    }
    
    msg_id, data, dlc = encode_func("MotorolaIntelMsg", values)
    assert msg_id == 0x123
    assert dlc == 8
    assert len(data) == 8
    
    # Check data bytes:
    # Speed_LE (1000 = 0x03E8) at byte 0, 1: byte 0 = 0xE8, byte 1 = 0x03
    assert data[0] == 0xE8
    assert data[1] == 0x03
    
    # RPM_BE (1000 = 0x03E8) at start_bit 23 (byte 2 bit 7): byte 2 = 0x03, byte 3 = 0xE8
    assert data[2] == 0x03
    assert data[3] == 0xE8
    
    # Temp_BE_Signed (-25 = 12-bit signed: 0xFE7):
    # start_bit 39 (byte 4 bit 7). Consumes byte 4 (8 bits: 0xFE), byte 5 upper 4 bits (0x7 << 4 = 0x70)
    assert data[4] == 0xFE
    assert (data[5] & 0xF0) == 0x70
    
    # Unaligned_BE (300 = 10-bit: 0x12C = 0b01_0010_1100):
    # start_bit 43 (byte 5 bit 3). Consumes byte 5 lower 4 bits (0b0100 = 4), byte 6 upper 6 bits (0b101100 << 2 = 0xB0)
    assert (data[5] & 0x0F) == 0x04
    assert (data[6] & 0xFC) == 0xB0
    
    # Now decode
    decoded = decode_func(0x123, data)
    assert decoded["message"] == "MotorolaIntelMsg"
    assert decoded["signals"]["Speed_LE"] == 1000.0
    assert decoded["signals"]["RPM_BE"] == 510.0
    assert decoded["signals"]["Temp_BE_Signed"] == -25.0
    assert decoded["signals"]["Unaligned_BE"] == 300.0


def test_micropython_can_generator_byteorder(db_session):
    gen = MicroPythonCanAppGenerator(db_session)
    code = gen.render(app_name="test_mpy_app")
    
    # Execute the generated code
    namespace = {}
    exec(code, namespace)
    
    encode_func = namespace["encode_message_by_name"]
    decode_func = namespace["decode_message_by_id"]
    
    values = {
        "Speed_LE": 1000.0,
        "RPM_BE": 510.0,
        "Temp_BE_Signed": -25.0,
        "Unaligned_BE": 300.0,
    }
    
    msg_id, data, dlc = encode_func("MotorolaIntelMsg", values)
    assert msg_id == 0x123
    assert dlc == 8
    
    # Verify decode
    decoded = decode_func(0x123, data)
    assert decoded["message"] == "MotorolaIntelMsg"
    assert decoded["signals"]["Speed_LE"] == 1000.0
    assert decoded["signals"]["RPM_BE"] == 510.0
    assert decoded["signals"]["Temp_BE_Signed"] == -25.0
    assert decoded["signals"]["Unaligned_BE"] == 300.0


def test_socketcan_c_generator_byteorder(db_session):
    gen = SocketCanCGenerator(db_session)
    code = gen.render(program_name="test_socketcan")
    
    assert "ins_bits_be" in code
    assert "ext_bits_be" in code
    assert "MotorolaIntelMsg" in code
    # Check that boolean le flag is generated properly (true for Speed_LE, false for RPM_BE)
    assert '"Speed_LE", 0, 16, true' in code
    assert '"RPM_BE", 23, 16, false' in code


def test_dsl_prototype_byteorder():
    dsl = DBC_DSL()
    with dsl.message("TestMsg", msg_id=0x200, dlc=8) as m:
        m.signal("SigLE", start=0, size=8, byte_order=ByteOrder.LITTLE_ENDIAN)
        m.signal("SigBE", start=15, size=8, byte_order=ByteOrder.BIG_ENDIAN)
    
    cg_msgs = to_cg_model(dsl)
    assert len(cg_msgs) == 1
    msg = cg_msgs[0]
    assert msg.signals[0].little_endian is True
    assert msg.signals[1].little_endian is False


def test_python_can_integration_byteorder(db_session):
    values = {
        "Speed_LE": 1000.0,
        "RPM_BE": 510.0,
        "Temp_BE_Signed": -25.0,
        "Unaligned_BE": 300.0,
    }
    
    msg_id, data, dlc = encode_message(db_session, "MotorolaIntelMsg", values)
    assert msg_id == 0x123
    assert dlc == 8
    
    decoded = decode_message(db_session, 0x123, data)
    assert decoded["message"] == "MotorolaIntelMsg"
    assert decoded["signals"]["Speed_LE"] == 1000.0
    assert decoded["signals"]["RPM_BE"] == 510.0
    assert decoded["signals"]["Temp_BE_Signed"] == -25.0
    assert decoded["signals"]["Unaligned_BE"] == 300.0
