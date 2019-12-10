import os

import pytest

from server import app
from utility import setup_logging


@pytest.fixture
def client():
	os.environ["BEE_API_CONF"] = "conf.json"  # For conf loading
	setup_logging("DEBUG", "test_log.txt")
	app.config["TESTING"] = True

	with app.test_client() as client:
		yield client
