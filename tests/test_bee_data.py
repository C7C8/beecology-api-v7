import json

from flask.testing import FlaskClient
from datetime import datetime
from client import client


def test_beedex_one(client: FlaskClient):
	# Base tests -- message must conform to expected response format
	res = client.get("/api_v7/api/BeeDex/5")
	assert res.status_code == 200
	data = json.loads(res.data)
	assert data["status"] == "success"
	assert data["message"] == "Retrieve the Bee information success!"
	assert not data["error"]
	assert len(data["data"]) > 0

	# Data entry must have needed data
	for datum in data["data"]:
		assert type(datum["bee_id"]) == int
		assert type(datum["bee_name"]) == str
		assert type(datum["common_name"]) == str
		assert type(datum["description"]) == str
		assert type(datum["confused"]) == str
		assert type(datum["confused"]) == str
		assert type(datum["bee_pic_path"]) == str
		assert "abdomen_list" in datum
		assert "thorax_list" in datum
		assert "head_list" in datum


def test_beedex_all(client: FlaskClient):
	res = client.get("/api_v7/api/BeeDex")
	assert res.status_code == 200
	data = json.loads(res.data)
	assert data["status"] == "success"
	assert data["message"] == "Retrieve the Bee information success!"
	assert not data["error"]
	assert len(data["data"]) > 0


def test_beedex_none(client: FlaskClient):
	res = client.get("/api_v7/api/BeeDex/999999")
	assert res.status_code == 404


def test_beevisrecords(client: FlaskClient):
	res = client.get("/api_v7/api/beevisrecords")
	assert res.status_code == 200
	data = json.loads(res.data)
	assert data["status"] == "success"
	assert data["message"] == "Retrieve the Bee records success!"
	assert not data["error"]
	assert len(data["data"]) > 0

	# Verify all needed fields are present in every object in the data list
	for datum in data["data"]:
		for field in ["bee_name", "loc_info", "flower_shape", "flower_name", "flower_color", "bee_behavior", "spgender", "elevation", "gender", "date"]:
			assert field in datum
			assert type(datum[field]) == str or datum[field] is None

		# Date must follow specific format
		try:
			datetime.strptime(datum["date"], "%Y-%m-%dT%H:%M:%S.%fZ")
		except ValueError:
			assert False
