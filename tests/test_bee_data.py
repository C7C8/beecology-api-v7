import json
import re

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


def test_beerecords(client: FlaskClient):
	res = client.get("/api_v7/api/beerecords/1")
	assert res.status_code == 200
	data = json.loads(res.data)
	assert data["status"] == "success"
	assert data["message"] == "Retrieve the Bee records success!"
	assert not data["error"]
	assert 0 < len(data["data"]) <= 50

	# Verify all needed fields are present in every object in the data list
	version_matcher = re.compile("^\d+\.\d+\.\d+$")
	for datum in data["data"]:
		# Strings:
		for field in ["bee_name", "coloration_abdomen", "coloration_thorax", "coloration_head", "flower_shape", "flower_color",
		              "time", "loc_info", "user_id", "record_pic_path", "record_video_path", "flower_name", "city_name",
		              "gender", "bee_behavior", "common_name", "app_version", "elevation"]:
			assert field in datum
			assert type(datum[field]) == str or datum[field] is None

		# Numbers
		for field in ["beerecord_id", "bee_dict_id"]:
			assert field in datum
			assert type(datum[field]) == int or datum[field] is None

		# Date must follow specific format
		try:
			datetime.strptime(datum["time"], "%Y-%m-%dT%H:%M:%S.%fZ")
		except ValueError:
			assert False

		# App version must follow specific format
		assert len(version_matcher.findall(datum["app_version"])) == 1


def test_beerecord_get(client: FlaskClient):
	"""Test beerecord endpoint; yes, there's more than one..."""
	res = client.get("/api_v7/api/beerecord/122")
	assert res.status_code == 200
	data = json.loads(res.data)
	assert data["status"] == "success"
	assert data["message"] == "Retrieve the Bee records success!"
	assert not data["error"]
	assert len(data["data"]) == 1
	data = data["data"][0]

	for field in ["user_id", "bee_name", "coloration_head", "coloration_abdomen", "coloration_thorax",
	            "gender", "flower_name", "city_name", "flower_shape", "flower_color", "loc_info", "date", "bee_behavior",
	            "record_pic_path", "record_video_path"]:
		assert field in data
		assert type(data[field]) == str

	for field in ["beerecord_id", "bee_dict_id"]:
		assert field in data
		assert type(data[field]) == int

	# Date must follow specific format
	try:
		datetime.strptime(data["date"], "%Y-%m-%dT%H:%M:%S.%fZ")
	except ValueError:
		assert False


def test_beerecord_crud(client: FlaskClient):
	"""Full test of beerecord CRUD abilities"""
	# TODO implement once beerecord upload is enabled
	pass
