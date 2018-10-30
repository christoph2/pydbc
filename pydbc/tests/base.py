
import unittest

from pydbc.api.db import Database
from pydbc.api.db import BaseObject


class BaseTest(unittest.TestCase):

    def setUp(self):
        self.db = Database("test", inMemory = True)

    def tearDown(self):
        self.db.close()

