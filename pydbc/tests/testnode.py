
from pprint import pprint
import unittest

from pydbc.api.db import Database
from pydbc.api.db import BaseObject


class TestCreation(unittest.TestCase):

  def setUp(self):
    self.db = Database("test", inMemory = True)
    
  def tearDown(self):
    self.db.close()

  def testDummyNodeExists(self):
    node = list(self.db.nodes())[0]
    self.assertEqual(node.name, "Vector__XXX")
    self.assertEqual(node.comment, "Dummy node for non-existent senders/receivers.")

  def testInsertNodeWorkx(self):
    self.db.addNode("ABC", "test-node")
    node = self.db.node("ABC")
    self.assertEqual(node.name, "ABC")
    self.assertEqual(node.comment, "test-node")
    
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
    äattr = n.attribute("NmJ1939IndustryGroup")
    attr = n.attribute("ECU")
    print(attr)
    self.db.db.commitTransaction()
    
if __name__ == '__main__':
  unittest.main()

  