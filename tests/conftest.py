import os
import tempfile
from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

os.environ.setdefault("SESSION_SECRET", "test-secret")


@pytest.fixture
def client() -> Iterator[TestClient]:
    """A TestClient backed by a fresh, empty SQLite file per test."""
    with tempfile.NamedTemporaryFile(suffix=".db") as db_file:
        os.environ["DB_PATH"] = db_file.name

        # Imported here, after DB_PATH is set, since apps.main reads it at
        # import time via the lifespan startup hook.
        from apps.main import app

        with TestClient(app) as test_client:
            yield test_client
