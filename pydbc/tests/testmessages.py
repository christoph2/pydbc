
from pprint import pprint
import unittest

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
        self.assertEqual(msg.name, "MSG")
        self.assertEqual(msg.identifier, 0x0815)
        self.assertEqual(msg.dlc, 4)
        self.assertEqual(msg.comment, "test-message")

    def testInsertDuplicateMessageFails(self):
        msg1 = self.createMessage()
        self.assertRaises(DuplicateKeyError, self.createMessage)

    def testNewlyCreatedMessageHasNoSignals(self):
        msg = self.createMessage()
        signals = list(msg.signals())
        self.assertEqual(signals, [])

    def testAddSignalWorks(self):
        msg = self.createMessage()
        signal = msg.addSignal("Drehzahl", 4, 8, ByteOrderType.INTEL, SignalType.UINT, "rpm", Formula(), Limits())
        #formula, limits,  multiplexing = MultiplexingType.NONE, values = None, comment = None

    def testSignalTypeUintWorks(self):
        msg = self.createMessage()
        signal = msg.addSignal("Drehzahl", 4, 8, ByteOrderType.INTEL, SignalType.UINT, "rpm", Formula(), Limits())
        self.assertEqual(signal.valueType, SignalType.UINT)

    def testSignalTypeSintWorks(self):
        msg = self.createMessage()
        signal = msg.addSignal("Drehzahl", 4, 8, ByteOrderType.INTEL, SignalType.SINT, "rpm", Formula(), Limits())
        self.assertEqual(signal.valueType, SignalType.SINT)

    def testSignalTypeFloat32Works(self):
        msg = self.createMessage()
        signal = msg.addSignal("Drehzahl", 4, 8, ByteOrderType.INTEL, SignalType.FLOAT32, "rpm", Formula(), Limits())
        self.assertEqual(signal.valueType, SignalType.FLOAT32)

    def testSignalTypeFloat64Works(self):
        msg = self.createMessage()
        signal = msg.addSignal("Drehzahl", 4, 8, ByteOrderType.INTEL, SignalType.FLOAT64, "rpm", Formula(), Limits())
        self.assertEqual(signal.valueType, SignalType.FLOAT64)

    def testUpdateWorks(self):
        msg = self.createMessage()
        msg.name = "MSG2"
        msg.identifier = 0x4711
        msg.dlc = 8
        msg.comment = "hello"
        msg.update()
        self.assertEqual(msg.name, "MSG2")
        self.assertEqual(msg.identifier, 0x4711)
        self.assertEqual(msg.dlc, 8)
        self.assertEqual(msg.comment, "hello")

    def testUpdateFails(self):
        msg = self.createMessage()
        msg2 = self.db.addMessage("MSG2", 0x4711, 8)
        msg2.name = "MSG"
        msg2.dlc = 7
        self.assertRaises(DuplicateKeyError, msg2.update)



