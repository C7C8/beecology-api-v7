import json
import os
from typing import Dict

import pytest
from flask import Response

from server import app
from utility import setup_logging, load_conf


@pytest.fixture
def client():
	os.environ["BEE_API_CONF"] = "conf.yml"  # For conf loading
	conf = load_conf()
	conf["testing"] = True
	setup_logging(conf["logging"])
	app.config["TESTING"] = True

	with app.test_client() as client:
		yield client


def check_ok_response(res: Response, message: str, code: int = 200) -> Dict:
	"""Helper to check common response attributes"""
	assert res.status_code == code
	data = json.loads(res.data)
	assert data["status"] == "success"
	assert data["message"] == message
	assert not data["error"]
	return data

def check_err_response(res: Response, message: str, code: int) -> Dict:
	"""Helper to check common error response attributes"""
	assert res.status_code == code
	data = json.loads(res.data)
	assert data["status"] == "false"
	assert data["message"] == message
	assert data["error"]
	return data
