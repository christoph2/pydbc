
import pytest

from pydbc.api.db import Database
from pydbc.api.db import BaseObject


class BaseTest:

    @pytest.fixture(autouse = True)
    def setup_database(self, db_in_memory):
        self.db = db_in_memory

