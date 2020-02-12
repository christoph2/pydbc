
from pydbc import types

def test_j1939_address():
    j0 = types.J1939Address.from_int(217056510)
    print(j0)
    assert j0.priority == 3
    assert j0.reserved == 0
    assert j0.datapage == 0
    assert j0.pdu_format == 240
    assert j0.pdu_specific == 4
    assert j0.source_address == 254
    assert j0.pgn == 61444
    assert j0.canID == 217056510

def test_j1939_set_pgn():
    j0 = types.J1939Address.from_int(217056510)
    j0.pgn = 64850
    assert j0.canID == 217928446
    assert j0.pgn == 64850

def test_j1939_str(capsys):
    j0 = types.J1939Address.from_int(419283454)
    print(str(j0))
    captured = capsys.readouterr()
    assert captured.out == "J1939Address(priority = 6, reserved = 0, datapage = 0, pdu_format = 253, pdu_specific = 193, source_address = 254)\n"

def test_j1939_repr(capsys):
    j0 = types.J1939Address.from_int(419283454)
    print(repr(j0))
    captured = capsys.readouterr()
    assert captured.out == "J1939Address(priority = 6, reserved = 0, datapage = 0, pdu_format = 253, pdu_specific = 193, source_address = 254)\n"

