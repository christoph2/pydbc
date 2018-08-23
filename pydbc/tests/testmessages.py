
from pprint import pprint
import unittest

from pydbc.tests.base import BaseTest
from pydbc.api.db import DuplicateKeyError


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
        signal = msg.addSignal()


