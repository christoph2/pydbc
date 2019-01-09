

import pytest

from pydbc.api.attribute import AttributeDefinition, Value, AttributeValue, Limits
from pydbc.exceptions import RangeError


class TestLimits(object):

    def testEmptyConstructorWorks(self):
        """Test default for `min` and `max` shall be 0.
        """
        l = Limits()
        assert l.min == 0
        assert l.max == 0

    def testConstructorWorks1(self):
        l = Limits(10, 20)
        assert l.min == 10
        assert l.max == 20

    def testConstructorWorks2(self):
        l = Limits(10.0, 20.0)
        assert l.min == 10.0
        assert l.max == 20.0

    def testConstructorWorks3(self):
        l = Limits(None, None)
        assert l.min == None
        assert l.max == None

    def testConstructorFails1(self):
        with pytest.raises(TypeError):
            l = Limits("hello", "world")

    def testAssignmentWorks1(self):
        l = Limits(90, 100)
        assert l.min == 90
        assert l.max == 100
        l.min = 10
        l.max = 20
        assert l.min == 10
        assert l.max == 20

    def testAssignmentWorks2(self):
        l = Limits(90, 100)
        assert l.min == 90
        assert l.max == 100
        l.min = 10.0
        l.max = 20.0
        assert l.min == 10.0
        assert l.max == 20.0

    def testAssignmentWorks3(self):
        l = Limits(90, 100)
        assert l.min == 90
        assert l.max == 100
        l.min = None
        l.max = 20.0
        assert l.min == None
        assert l.max == 20.0

    def testAssignmentWorks4(self):
        l = Limits(90, 100)
        assert l.min == 90
        assert l.max == 100
        l.min = 10.0
        l.max = None
        assert l.min == 10.0
        assert l.max == None

    def testMaxShallGreaterThanMin1(self):
        with pytest.raises(RangeError):
            l = Limits(100, 0)

    def testEquality(self):
        l0 = Limits(-10, 10)
        l1 = Limits(-10, 10)
        assert l0 == l1

    def testUnequality(self):
        l0 = Limits(-10, 10)
        l1 = Limits(-5, 5)
        assert l0 != l1


