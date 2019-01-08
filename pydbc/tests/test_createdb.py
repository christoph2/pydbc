
import unittest

from pydbc.api.db import Database


class TestCreation(unittest.TestCase):

  def testCreateDatabase(self):
    db = Database("test")
    
    
if __name__ == '__main__':
  unittest.main()