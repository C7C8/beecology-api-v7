import json
from logging import getLogger

from flask_restplus import Resource, reqparse

from beecology_api import config
from beecology_api.api.authentication import authenticate, admin_required
from beecology_api.api.response import response

log = getLogger()


class News(Resource):
	@staticmethod
	def get():
		try:
			with open("{}/news.json".format(config.config["news"]["folder"]), "r") as file:
				return response("success", "Retrieve the News information success!", True, data=json.load(file))
		except IOError as e:
			log.error("Failed to load news file {}/news.json: {}".format(config.config["news"]["folder"], e))
			return response("false", "Failed to load news file", True), 500

	@staticmethod
	@authenticate
	@admin_required
	def put():
		parser = reqparse.RequestParser()
		parser.add_argument("json", type=dict, required=True)
		args = parser.parse_args()

		return update_news_file(args["json"], "news.json")


class BioCSNews(Resource):
	@staticmethod
	def get():
		try:
			with open("{}/biocsnews.json".format(config.config["news"]["folder"]), "r") as file:
				return response("success", "Retrieve the BIO-CS News information success!", True, data=json.load(file))
		except IOError as e:
			log.error("Failed to load news file {}/biocsnews.json: {}".format(config.config["news"]["folder"], e))
			return response("false", "Failed to load news file", True), 500

	@staticmethod
	@authenticate
	@admin_required
	def put():
		"""Update Bio/CS news"""
		parser = reqparse.RequestParser()
		parser.add_argument("json", type=dict, required=True)
		args = parser.parse_args()

		return update_news_file(args["json"], "biocsnews.json")


def update_news_file(news, filename):
	try:
		with open("{}/{}".format(config.config["storage"]["news-path"], filename), "w") as file:
			json.dump(news, file)
	except IOError as e:
		log.error("Failed to save bio/cs news update to {}: {}".format(config.config["news"]["folder"], e))
		return "Failed to save news update", 500
	return response("success", "Updated news", False)
