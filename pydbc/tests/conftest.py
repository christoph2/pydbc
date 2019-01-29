
import pytest

from pydbc.api.db import Database
from pydbc.api.db import BaseObject


@pytest.fixture(scope = "function")
def db_in_memory():
    db = Database("test", inMemory = True)
    yield db
    db.close()

