import json
import re

from flask.testing import FlaskClient
from datetime import datetime
from client import client

from tests.client import check_ok_response, check_err_response


def test_beedex_one(client: FlaskClient):
	# Base tests -- message must conform to expected response format
	res = client.get("/api_v7/api/beedex/5")
	data = check_ok_response(res, "Retrieve the Bee information success!")
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
	res = client.get("/api_v7/api/beedex")
	data = check_ok_response(res, "Retrieve the Bee information success!")
	assert len(data["data"]) > 0


def test_beedex_none(client: FlaskClient):
	res = client.get("/api_v7/api/beedex/999999")
	check_err_response(res, "Bee Dexes not found!", 404)


def test_beevisrecords(client: FlaskClient):
	res = client.get("/api_v7/api/beevisrecords")
	data = check_ok_response(res, "Retrieve the Bee records success!")
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
	data = check_ok_response(res, "Retrieve the Bee records success!")
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


def test_beerecord_crud(client: FlaskClient):
	"""Full test of beerecord CRUD abilities"""
	# Dummy bee record
	bee_record = {
		"elevation": 30,
		"chead": "test head",
		"cabdomen": "test abdomen",
		"cthorax": "test thorax",
		"gender": "female",
		"loc": "40 40",
		"cityname": "Worcester MA",
		"fname": "im a flower watch me go",
		"fshape": "flower shape",
		"fcolor": "red",
		"beename": "im a bee! bzzz",
		"time": "2019-12-19T20:43:52.243Z",
		"beedictid": "1",
		"beebehavior": "1",
		"recordpicpath": "picture.bmp",
		"appversion": "1.2.2",
	}

	# Post a new bee record
	res = client.post("/api_v7/api/record", data=bee_record)
	data = check_ok_response(res, "Log a new bee success!")
	assert len(data["data"]) == 1
	id = data["data"][0]["beerecord_id"]

	# Retrieve the same bee record to make sure it got added
	res = client.get("/api_v7/api/beerecord/{}".format(id))
	data = check_ok_response(res, "Retrieve the Bee records success!")
	assert len(data["data"]) == 1
	assert data["data"][0]["beerecord_id"] == id

	# Update the bee record with new data
	res = client.put("/api_v7/api/beerecord/{}".format(id), data={"beename": "im another bee! BZZ"})
	data = check_ok_response(res, "Retrieve the Bee information success!")
	assert len(data["data"]) == 1
	assert data["data"][0]["beerecord_id"] == id

	# Check to make sure the record was updated
	res = client.get("/api_v7/api/beerecord/{}".format(id))
	data = check_ok_response(res, "Retrieve the Bee records success!")
	assert len(data["data"]) == 1
	assert data["data"][0]["beerecord_id"] == id
	assert data["data"][0]["bee_name"] == "im another bee! BZZ"

	# Delete the record
	res = client.delete("/api_v7/api/beerecord/{}".format(id))
	data = check_ok_response(res, "Delete record success!")
	assert len(data["data"]) == 1
	assert data["data"][0]["beerecord_id"] == id

	# Updating the record should return an error
	res = client.put("/api_v7/api/beerecord/{}".format(id), data={"beename": "im another bee! BZZ"})
	check_err_response(res, "Bee Dexes not found!", 404)

	# Getting the record should return an error
	res = client.get("/api_v7/api/beerecord/{}".format(id))
	check_err_response(res, "Bee Records not found!", 404)

	# Deleting the record should return an error
	res = client.delete("/api_v7/api/beerecord/{}".format(id))
	check_err_response(res, "Bee record id not found!", 404)

