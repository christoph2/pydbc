
from pprint import pprint
import unittest

from pydbc.tests.base import BaseTest
from pydbc.api.db import DuplicateKeyError


class TestNode(BaseTest):

  def testDummyNodeExists(self):
    node = list(self.db.nodes())[0]
    self.assertEqual(node.name, "Vector__XXX")
    self.assertEqual(node.comment, "Dummy node for non-existent senders/receivers.")

  def testInsertNodeWorkx(self):
    self.db.addNode("ABC", "test-node")
    node = self.db.node("ABC")
    self.assertEqual(node.name, "ABC")
    self.assertEqual(node.comment, "test-node")

  def testNodeNameShallBeUnique(self):
    self.db.addNode("ABC", "test-node")
    self.assertRaises(DuplicateKeyError, self.db.addNode, "ABC", "test-node")

  def testNodeDeletionWorkx(self):
    self.db.addNode("ABC", "test-node")
    node = self.db.node("ABC")
    node.remove()
    node = self.db.node("ABC")
    self.assertIsNone(node)

  def testUpdateWorkx(self):
    self.db.addNode("ABC", "test-node")
    node = self.db.node("ABC")
    node.name = "DEF"
    node.comment = "foo bar"
    node.update()
    node = self.db.node("ABC")
    self.assertIsNone(node)
    node = self.db.node("DEF")
    self.assertEqual(node.name, "DEF")
    self.assertEqual(node.comment, "foo bar")

  def testUpdateFails1(self):
    self.db.addNode("ABC", "test-node")
    self.db.addNode("DEF", "test-node")
    node = self.db.node("ABC")
    node.name = "DEF"
    self.assertRaises(DuplicateKeyError, node.update)

  def testUpdateFails2(self):
    self.db.addNode("ABC", "test-node")
    node = self.db.node("ABC")
    self.assertRaises(TypeError, node.name, 45.35)

  def testUpdateFails3(self):
    self.db.addNode("ABC", "test-node")
    node = self.db.node("ABC")
    self.assertRaises(TypeError, node.comment, 47.11)

  def testRidCouldNotBeSet(self):
    self.db.addNode("ABC", "test-node")
    node = self.db.node("ABC")
    try:
      node.rid = 0
    except AttributeError:
      pass
    except Exception as e:
      raise

  def testDatabaseCouldNotBeSet(self):
    self.db.addNode("ABC", "test-node")
    node = self.db.node("ABC")
    try:
      node.database = None
    except AttributeError:
      pass
    except Exception:
      raise

  @unittest.skip
  def testNodeAttrs(self):
    #nodes = [n for n in self.db.nodes(regex = ".*Unit")]
    nodes = [n for n in self.db.nodes()]
    print(nodes)
    n0= nodes[0]
    n0.comment = "Hello world comment!!!"
    print("\n\n\n", n0.name)
    for n in nodes:
      print("***", n.name)
      for attr in n.attributes:
        print(attr)
    print("AV:", attr.value)
    attr.value = "TestECU"
    print("New AV:", attr)
    attr.update()
    attr = n.attribute("NmJ1939IndustryGroup")
    attr = n.attribute("ECU")
    print(attr)
    self.db.db.commitTransaction()

if __name__ == '__main__':
  unittest.main()

