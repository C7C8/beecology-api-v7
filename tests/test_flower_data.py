import json

from flask.testing import FlaskClient
from client import client

from tests.client import check_ok_response, check_err_response


def test_flowerdex_one(client: FlaskClient):
	# Base tests -- message must conform to expected response format
	res = client.get("/api_v7/api/flowerdex/5")
	data = check_ok_response(res, "Retrieve the Flower information success!")
	assert len(data["data"]) > 0

	# Data entry must have needed data
	entry = data["data"][0]
	assert type(entry["flower_id"]) == int
	assert type(entry["flower_latin_name"]) == str
	assert type(entry["flower_common_name"]) == str


def test_flowerdex_all(client: FlaskClient):
	res = client.get("/api_v7/api/flowerdex")
	data = check_ok_response(res, "Retrieve the Flower information success!")
	assert len(data["data"]) > 0


def test_flowerdex_none(client: FlaskClient):
	res = client.get("/api_v7/api/flowerdex/999999")
	check_err_response(res, "Flower not found!", 404)


def test_flower_shapes(client: FlaskClient, url=None):
	res = client.get("/api_v7/api/flowershapes" if url is None else url)
	data = check_ok_response(res, "Retrieve the flower shapes success!")
	assert len(data["data"]) > 0

	# All fields must be of the right type, must only return flower features
	for datum in data["data"]:
		for field in ["feature_id", "feature_name", "feature_description", "feature_pic_path"]:
			assert field in datum
			assert type(datum[field]) == str
		assert datum["feature_id"].startswith("fc")


def test_flower_colors(client: FlaskClient):
	# Flower shapes and flower colors endpoints do the same. exact. thing.
	test_flower_shapes(client, url="/api_v7/api/flowercolors")


def test_unmatched_flowers(client: FlaskClient):
	res = client.get("/api_v7/api/unmatched_flowers")
	data = check_ok_response(res, "Retrieve the Bee records success!")  # TODO This... is not the right response.
	assert len(data["data"]) > 0

	for datum in data["data"]:
		for field in ["flower_name", "count"]:
			assert field in datum
			assert type(field) == str

		int(datum["count"])  # Will throw an exception if the field can't be parsed into an int


def test_insert_delete_flower(client: FlaskClient):
	# Send a request and make sure the server reports success
	res = client.post("/api_v7/api/flowerdex", data={
		"flowercommonname": "Test Flower",
		"flowershapeid": "fs2",
		"flowercolorid": "fc6",
		"flowerspecies": "Testificus",
		"flowergenus": "Unit"
	})
	data = check_ok_response(res, "Log a new flower success!")
	id = data["data"]["flower_id"]
	assert id > 0

	# Try updating the flower
	# TODO Find a way to automate checking database contents, since the API doesn't expose
	res = client.put("/api_v7/api/flowerdex/{}".format(id), data={
		"fcommon": "Test flower update"
	})
	data = check_ok_response(res, "Update the Folwer information success!")
	assert data["data"]["flower_id"] == id

	# Clean up -- delete the flower we just created
	res = client.delete("/api_v7/api/flowerdex/{}".format(id))
	check_ok_response(res, "Delete flower success!")

	# Try to delete the flower we just deleted, we should get an error
	res = client.delete("/api_v7/api/flowerdex/{}".format(id))
	check_err_response(res, "flower id not found!", 404)

	# Try to update the flower we just deleted, we should get an error
	res = client.put("/api_v7/api/flowerdex/{}".format(id), data={
		"fcommon": "This flower doesn't exist"
	})
	check_err_response(res, "Flower not found!", 404)
