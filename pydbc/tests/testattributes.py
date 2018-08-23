from pprint import pprint
import unittest

from pydbc.tests.base import BaseTest
from pydbc.api.db import DuplicateKeyError
from pydbc.types import AttributeType, ValueType
from pydbc.api.limits import Limits


class TestAttributes(BaseTest):

    def createAttribute(self):
      return self.db.addAttributeDefinition("ABC", AttributeType.NODE, ValueType.INT, 0, Limits(-10, 10), comment ="hello")

    def testAddWorkx(self):
      attr = self.createAttribute()
      self.assertEqual(attr.name ,"ABC" )
      self.assertEqual(attr.objectType, AttributeType.NODE)
      self.assertEqual(attr.valueType, ValueType.INT)
      self.assertEqual(attr.limits, Limits(-10, 10))
      self.assertEqual(attr.default, 0)
      self.assertEqual(attr.values, [])
      self.assertEqual(attr.comment, "hello")

    @unittest.skip
    def testUpdateWorkx(self):
        attr = self.createAttribute()
        attr.comment = "world"
        attr.valueType = ValueType.FLOAT
        attr.objectType = AttributeType.ENV_VAR
        attr.update()
        attr = self.db.AttributeDefinition("ABC")
        self.assertEqual(attr.objectType, AttributeType.ENV_VAR)
        self.assertEqual(attr.valueType, ValueType.FLOAT)
        self.assertEqual(attr.comment, "world")

    def testUpdateFails(self):
        pass

    def testRidCouldNotBeSet(self):
      attr = self.createAttribute()
      try:
          attr.rid = 0
      except AttributeError:
          pass
      except Exception as e:
          raise

    def testDatabaseCouldNotBeSet(self):
      attr = self.createAttribute()
      try:
          attr.database = None
      except AttributeError:
          pass
      except Exception:
          raise

    def testSetNameWorks(self):
        attr = self.createAttribute()
        attr.name = "DEF"
        self.assertEqual(attr.name, "DEF")

    def testSetNameFails(self):
        attr = self.createAttribute()
        self.assertRaises(TypeError, attr.name, 4711)

    def testSetObjectTypeWorks1(self):
        attr = self.createAttribute()
        attr.objectType = 4
        self.assertEqual(attr.objectType, 4)

    def testSetObjectTypeWorks2(self):
        attr = self.createAttribute()
        attr.objectType = AttributeType.NODE
        self.assertEqual(attr.objectType, AttributeType.NODE)

    def testSetObjectTypeFails1(self):
        attr = self.createAttribute()
        try:
            attr.objectType = 112
        except ValueError:
            pass
        except Exception:
            raise

    def testSetObjectTypeFail21(self):
        attr = self.createAttribute()
        try:
            attr.objectType = "hello"
        except ValueError:
            pass
        except Exception:
            raise

    def testSetLimitsWorks(self):
        attr = self.createAttribute()
        attr.limits = Limits(-1, 1)
        self.assertEqual(attr.limits, Limits(-1, 1))

    def testSetLimitsFails(self):
        attr = self.createAttribute()
        self.assertRaises(TypeError, attr.limits, "Hello, world")

    def testSetCommentWorks(self):
        attr = self.createAttribute()
        attr.comment = "world"
        self.assertEqual(attr.comment, "world")

    def testSetCommentFails(self):
        attr = self.createAttribute()
        self.assertRaises(TypeError, attr.comment, 4711)

    def testSettingWorkAttributeWorks1(self):
        attr = self.createAttribute()
        node = self.db.addNode("XXX", "test-node")
        av = node.attribute("ABC")
        av.value = 10

if __name__ == '__main__':
  unittest.main()
