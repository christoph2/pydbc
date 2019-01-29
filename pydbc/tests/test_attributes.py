from pprint import pprint

import pytest

from pydbc.tests.base import BaseTest
from pydbc.api.db import DuplicateKeyError
from pydbc.api.attribute import AttributeDefinition
from pydbc.types import AttributeType, ValueType
from pydbc.api.limits import Limits


class TestAttributes(BaseTest):

    def createAttribute(self):
      return self.db.addAttributeDefinition("ABC", AttributeType.NODE, ValueType.INT, 0, Limits(-10, 10), comment ="hello")

    def testAddWorkx(self):
      attr = self.createAttribute()
      assert attr.name == "ABC"
      assert attr.objectType == AttributeType.NODE
      assert attr.valueType == ValueType.INT
      assert attr.limits == Limits(-10, 10)
      assert attr.default == 0
      assert attr.values == []
      assert attr.comment == "hello"

    def testUpdateWorkx(self):
        attr = self.createAttribute()
        attr.comment = "world"
        attr.valueType = ValueType.FLOAT
        attr.objectType = AttributeType.ENV_VAR
        attr.update()
        attr = AttributeDefinition(self.db, 42, "ABC", AttributeType.ENV_VAR, ValueType.FLOAT, 0, comment ="world")
        assert attr.objectType == AttributeType.ENV_VAR
        assert attr.valueType == ValueType.FLOAT
        assert attr.comment == "world"

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
        assert attr.name == "DEF"

    def testSetNameFails(self):
        attr = self.createAttribute()
        with pytest.raises(TypeError):
            attr.name = 4711

    def testSetObjectTypeWorks1(self):
        attr = self.createAttribute()
        attr.objectType = 4
        assert attr.objectType == 4

    def testSetObjectTypeWorks2(self):
        attr = self.createAttribute()
        attr.objectType = AttributeType.NODE
        assert attr.objectType == AttributeType.NODE

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
        assert attr.limits == Limits(-1, 1)

    def testSetLimitsFails(self):
        attr = self.createAttribute()
        with pytest.raises(TypeError):
            attr.limits = "Hello, world"

    def testSetCommentWorks(self):
        attr = self.createAttribute()
        attr.comment = "world"
        assert attr.comment == "world"

    def testSetCommentFails(self):
        attr = self.createAttribute()
        with pytest.raises(TypeError):
            attr.comment = 4711

    def testSettingWorkAttributeWorks1(self):
        attr = self.createAttribute()
        node = self.db.addNode("XXX", "test-node")
        av = node.attribute("ABC")
        av.value = 10

