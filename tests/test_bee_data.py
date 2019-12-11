import json

from flask.testing import FlaskClient
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
	entry = data["data"][0]
	assert type(entry["bee_id"]) == int
	assert type(entry["bee_name"]) == str
	assert type(entry["common_name"]) == str
	assert type(entry["description"]) == str
	assert type(entry["confused"]) == str
	assert type(entry["confused"]) == str
	assert type(entry["bee_pic_path"]) == str
	assert "abdomen_list" in entry
	assert "thorax_list" in entry
	assert "head_list" in entry


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
