
from pprint import pprint
import pytest

from pydbc.tests.base import BaseTest
from pydbc.api.db import DuplicateKeyError
from pydbc.types import AttributeType, MultiplexingType, ValueTableType, ByteOrderType, ValueType, SignalType
from pydbc.api.signal import Formula
from pydbc.api.limits import Limits

class TestMessage(BaseTest):

    def createMessage(self):
        return self.db.addMessage("MSG", 0x0815, 4, "test-message")

    def testInsertMessageWorks(self):
        msg = self.createMessage()
        assert msg.name == "MSG"
        assert msg.identifier == 0x0815
        assert msg.dlc == 4
        assert msg.comment == "test-message"

    def testInsertDuplicateMessageFails(self):
        msg1 = self.createMessage()
        with pytest.raises(DuplicateKeyError):
            self.createMessage()

    def testNewlyCreatedMessageHasNoSignals(self):
        msg = self.createMessage()
        signals = list(msg.signals())
        assert signals == []

    def testAddSignalWorks(self):
        msg = self.createMessage()
        signal = msg.addSignal("Drehzahl", 4, 8, ByteOrderType.INTEL, SignalType.UINT, "rpm", Formula(), Limits())

    def testSignalTypeUintWorks(self):
        msg = self.createMessage()
        signal = msg.addSignal("Drehzahl", 4, 8, ByteOrderType.INTEL, SignalType.UINT, "rpm", Formula(), Limits())
        assert signal.valueType == SignalType.UINT

    def testSignalTypeSintWorks(self):
        msg = self.createMessage()
        signal = msg.addSignal("Drehzahl", 4, 8, ByteOrderType.INTEL, SignalType.SINT, "rpm", Formula(), Limits())
        assert signal.valueType == SignalType.SINT

    def testSignalTypeFloat32Works(self):
        msg = self.createMessage()
        signal = msg.addSignal("Drehzahl", 4, 8, ByteOrderType.INTEL, SignalType.FLOAT32, "rpm", Formula(), Limits())
        assert signal.valueType == SignalType.FLOAT32

    def testSignalTypeFloat64Works(self):
        msg = self.createMessage()
        signal = msg.addSignal("Drehzahl", 4, 8, ByteOrderType.INTEL, SignalType.FLOAT64, "rpm", Formula(), Limits())
        assert signal.valueType == SignalType.FLOAT64

    def testSignalByteOrderIntelWorks(self):
        msg = self.createMessage()
        signal = msg.addSignal("Drehzahl", 4, 8, ByteOrderType.INTEL, SignalType.UINT, "rpm", Formula(), Limits())
        assert signal.byteOrder == ByteOrderType.INTEL

    def testSignalByteOrderMotorolaWorks(self):
        msg = self.createMessage()
        signal = msg.addSignal("Drehzahl", 4, 8, ByteOrderType.MOTOROLA, SignalType.UINT, "rpm", Formula(), Limits())
        assert signal.byteOrder == ByteOrderType.MOTOROLA

    def testUpdateWorks(self):
        msg = self.createMessage()
        msg.name = "MSG2"
        msg.identifier = 0x4711
        msg.dlc = 8
        msg.comment = "hello"
        msg.update()
        assert msg.name == "MSG2"
        assert msg.identifier == 0x4711
        assert msg.dlc == 8
        assert msg.comment == "hello"

    def testUpdateFails(self):
        msg = self.createMessage()
        msg2 = self.db.addMessage("MSG2", 0x4711, 8)
        msg2.name = "MSG"
        msg2.dlc = 7
        with pytest.raises(DuplicateKeyError):
            msg2.update()



