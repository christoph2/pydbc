

import unittest
from unittest import mock

from pydbc.api.attribute import AttributeDefinition, Value, AttributeValue, Limits


class TestLimits(unittest.TestCase):

  def testEmptyConstructorWorks(self):
    l = Limits()

  def testConstructorWorks1(self):
    l = Limits(10, 20)

  def testConstructorWorks2(self):
    l = Limits(10.0, 20.0)

  def testConstructorWorks3(self):
    l = Limits(None, None)

  def testConstructorFails1(self):
    self.assertRaises(TypeError, Limits, "hello", "world")

  def testAssignmentWorks1(self):
    l = Limits(90, 100)
    l.min = 10
    l.max = 20

  def testAssignmentWorks2(self):
    l = Limits(90, 100)
    l.min = 10.0
    l.max = 20.0

  def testAssignmentWorks3(self):
    l = Limits(90, 100)
    l.min = None
    l.max = 20.0

  def testAssignmentWorks4(self):
    l = Limits(90, 100)
    l.min = 10.0
    l.max = None

  def testMaxShallGreaterThanMin1(self):
    self.assertRaises(ValueError, Limits, 100, 0)

  def testEquality(self):
    l0 = Limits(-10, 10)
    l1 = Limits(-10, 10)
    self.assertEqual(l0, l1)

  def testUnequality(self):
    l0 = Limits(-10, 10)
    l1 = Limits(-5, 5)
    self.assertNotEqual(l0, l1)

if __name__ == '__main__':
  unittest.main()
