import os

import pytest

from server import app
from utility import setup_logging, load_conf


@pytest.fixture
def client():
	os.environ["BEE_API_CONF"] = "conf.json"  # For conf loading
	conf = load_conf()
	setup_logging(conf["logging"])
	app.config["TESTING"] = True

	with app.test_client() as client:
		yield client
