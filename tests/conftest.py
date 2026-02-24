import copy

import pytest
from fastapi.testclient import TestClient

import src.app as app_module

# Snapshot of the original activities state, taken once at import time
_ORIGINAL_ACTIVITIES = copy.deepcopy(app_module.activities)


@pytest.fixture
def client():
    """
    Provide a TestClient with a freshly reset activities store before every test.

    The in-memory ``activities`` dict is restored to its original seeded state
    by clearing and repopulating the existing dict object in-place, so all
    references inside src/app.py keep pointing at the same object.
    """
    # Restore to clean state before each test
    app_module.activities.clear()
    app_module.activities.update(copy.deepcopy(_ORIGINAL_ACTIVITIES))

    with TestClient(app_module.app) as test_client:
        yield test_client
