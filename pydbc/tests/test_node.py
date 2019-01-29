
from pprint import pprint
import pytest

from pydbc.tests.base import BaseTest
from pydbc.api.db import DuplicateKeyError


class TestNode(BaseTest):

  def testDummyNodeExists(self):
    node = list(self.db.nodes())[0]
    assert node.name == "Vector__XXX"
    assert node.comment == "Dummy node for non-existent senders/receivers."

  def testInsertNodeWorkx(self):
    node = self.db.addNode("ABC", "test-node")
    assert node.name == "ABC"
    assert node.comment == "test-node"

  def testNodeNameShallBeUnique(self):
    self.db.addNode("ABC", "test-node")
    with pytest.raises(DuplicateKeyError):
        self.db.addNode("ABC", "test-node")

  def testNodeDeletionWorkx(self):
    node = self.db.addNode("ABC", "test-node")
    node.remove()
    node = self.db.node("ABC")
    assert node is None


  def testUpdateWorkx(self):
    node = self.db.addNode("ABC", "test-node")
    node.name = "DEF"
    node.comment = "foo bar"
    node.update()
    node = self.db.node("ABC")
    assert node is None
    node = self.db.node("DEF")
    assert node.name == "DEF"
    assert node.comment == "foo bar"


  def testUpdateFails1(self):
    node = self.db.addNode("ABC", "test-node")
    self.db.addNode("DEF", "test-node")
    node.name = "DEF"
    with pytest.raises(DuplicateKeyError):
        node.update()

  def testUpdateFails2(self):
    node = self.db.addNode("ABC", "test-node")
    with pytest.raises(TypeError):
        node.name = 45.35

  def testUpdateFails3(self):
    node = self.db.addNode("ABC", "test-node")
    with pytest.raises(TypeError):
        node.comment = 47.11

  def testRidCouldNotBeSet(self):
    node = self.db.addNode("ABC", "test-node")
    with pytest.raises(AttributeError):
      node.rid = 0

  def testDatabaseCouldNotBeSet(self):
    node = self.db.addNode("ABC", "test-node")
    with pytest.raises(AttributeError):
      node.database = None

  #  def testNodeAttrs(self):
  #    #nodes = [n for n in self.db.nodes(regex = ".*Unit")]
  #    nodes = [n for n in self.db.nodes()]
  #    print(nodes)
  #    n0= nodes[0]
  #    n0.comment = "Hello world comment!!!"
  #    print("\n\n\n", n0.name)
  #    for n in nodes:
  #      print("***", n.name)
  #      for attr in n.attributes:
  #        print(attr)
  #    print("AV:", attr.value)
  #    attr.value = "TestECU"
  #    print("New AV:", attr)
  #    attr.update()
  #    attr = n.attribute("NmJ1939IndustryGroup")
  #    attr = n.attribute("ECU")
  #    print(attr)
  #    self.db.db.commitTransaction()
