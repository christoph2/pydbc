
from pprint import pprint
import unittest

from pydbc.tests.base import BaseTest
from pydbc.api.db import DuplicateKeyError


class TestMessage(BaseTest):

  def testInsertMessageWorks(self):
      msg = self.db.addMessage("MSG", 0x0815, 4, "test-message")
      self.assertEqual(msg.name, "MSG")
      self.assertEqual(msg.identifier, 0x0815)
      self.assertEqual(msg.dlc, 4)
      self.assertEqual(msg.comment, "test-message")

