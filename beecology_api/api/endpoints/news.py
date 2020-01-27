import json
from logging import getLogger

from flask_restplus import Resource, reqparse

from beecology_api import config
from beecology_api.api.api import api
from beecology_api.api.authentication import authenticate, admin_required
from beecology_api.api.models import news_response, news_parser, response_wrapper
from beecology_api.api.response import response

log = getLogger()


class News(Resource):
	@api.response(200, "News enclosed", news_response)
	def get(self):
		"""Get current news"""
		try:
			with open("{}/news.json".format(config.config["news"]["folder"]), "r") as file:
				return response("success", "Retrieve the News information success!", True, data=json.load(file))
		except IOError as e:
			log.error("Failed to load news file {}/news.json: {}".format(config.config["news"]["folder"], e))
			return response("false", "Failed to load news file", True), 500

	@api.expect(news_parser)
	@api.response(200, "Updated news", response_wrapper)
	@authenticate
	@admin_required
	def put(self):
		"""Update news. Administrator access required."""
		args = news_parser.parse_args()
		return update_news_file(args["json"], "news.json")


class BioCSNews(Resource):
	@api.response(200, "Bio/CS news enclosed", news_response)
	def get(self):
		"""Get Bio/CS news."""
		try:
			with open("{}/biocsnews.json".format(config.config["news"]["folder"]), "r") as file:
				return response("success", "Retrieve the BIO-CS News information success!", True, data=json.load(file))
		except IOError as e:
			log.error("Failed to load news file {}/biocsnews.json: {}".format(config.config["news"]["folder"], e))
			return response("false", "Failed to load news file", True), 500

	@api.expect(news_parser)
	@api.response(200, "Updated news", response_wrapper)
	@authenticate
	@admin_required
	def put(self):
		"""Update Bio/CS news. Administrator access required."""
		args = news_parser.parse_args()
		return update_news_file(args["json"], "biocsnews.json")


def update_news_file(news, filename):
	try:
		with open("{}/{}".format(config.config["storage"]["news-path"], filename), "w") as file:
			json.dump(news, file)
	except IOError as e:
		log.error("Failed to save bio/cs news update to {}: {}".format(config.config["news"]["folder"], e))
		return "Failed to save news update", 500
	return response("success", "Updated news", False)
