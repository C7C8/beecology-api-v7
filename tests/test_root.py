import json

from flask.testing import FlaskClient
from client import client

def test_root(client: FlaskClient):
	"""Test base functionality -- getting from root should return 200 OK, a json object, with the given text."""
	res = client.get("/api_v7/api/")
	assert res.status_code == 200
	assert res.content_type == "application/json"
	loaded = json.loads(res.data)
	assert type(loaded) == dict
	assert loaded["message"] == "Welcome! The api is working!"


