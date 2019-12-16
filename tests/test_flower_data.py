import json

from flask.testing import FlaskClient
from client import client


def test_flowerdex_one(client: FlaskClient):
	# Base tests -- message must conform to expected response format
	res = client.get("/api_v7/api/flowerdex/5")
	assert res.status_code == 200
	data = json.loads(res.data)
	assert data["status"] == "success"
	assert data["message"] == "Retrieve the Flower information success!"
	assert not data["error"]
	assert len(data["data"]) > 0

	# Data entry must have needed data
	entry = data["data"][0]
	assert type(entry["flower_id"]) == int
	assert type(entry["flower_latin_name"]) == str
	assert type(entry["flower_common_name"]) == str


def test_flowerdex_all(client: FlaskClient):
	res = client.get("/api_v7/api/flowerdex")
	assert res.status_code == 200
	data = json.loads(res.data)
	assert data["status"] == "success"
	assert data["message"] == "Retrieve the Flower information success!"
	assert not data["error"]
	assert len(data["data"]) > 0


def test_flowerdex_none(client: FlaskClient):
	res = client.get("/api_v7/api/flowerdex/999999")
	assert res.status_code == 404


def test_flower_shapes(client: FlaskClient):
	res = client.get("/api_v7/api/flowershapes")
	assert res.status_code == 200
	data = json.loads(res.data)
	assert data["status"] == "success"
	assert data["message"] == "Retrieve the flower shapes success!"
	assert not data["error"]
	assert len(data["data"]) > 0

	# All fields must be of the right type, must only return flower features
	for datum in data["data"]:
		for field in ["feature_id", "feature_name", "feature_description", "feature_pic_path"]:
			assert field in datum
			assert type(datum[field]) == str
		assert datum["feature_id"].startswith("fc")
