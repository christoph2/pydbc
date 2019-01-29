
import pytest

from pydbc.api.db import Database


class TestCreation:

    def testCreateDatabase(self):
        db = Database("test")
        assert db.dbname == "test.vndb"
        assert db.dbtype == "CAN"
