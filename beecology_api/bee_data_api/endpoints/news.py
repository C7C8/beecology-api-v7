import json
from logging import getLogger

from flask_restx import Resource

from beecology_api import config
from beecology_api.bee_data_api.api import api
from beecology_api.bee_data_api.authentication import admin_required
from beecology_api.bee_data_api.models import news_response, news_parser, response_wrapper
from beecology_api.bee_data_api.response import response

log = getLogger()

# Multiple classes are required so that Swagger docs aren't generated for methods that aren't supposed to exist (e.g.
# GET on /update_biocsnews

class GetNews(Resource):
	@api.response(200, "News enclosed", news_response)
	def get(self):
		"""Get current news. News is contained in the `data` field of the response."""
		data = {}
		try:
			with open("{}/news.json".format(config.config["storage"]["news-path"]), "r") as file:
				data = json.load(file)
		except IOError as e:
			log.warning("Failed to load news file {}/news.json, returning default response. Error: {}".format(config.config["storage"]["news-path"], e))
		return response("success", "Retrieve the News information success!", True, data=data), 200


class UpdateNews(Resource):
	@api.expect(news_parser)
	@api.response(200, "Updated news", response_wrapper)
	@admin_required
	def put(self):
		"""Update news. Administrator access required."""
		args = news_parser.parse_args()
		return update_news_file(args["json"], "news.json")


class GetBioCSNews(Resource):
	@api.response(200, "Bio/CS news enclosed", news_response)
	def get(self):
		"""Get Bio/CS news. News is contained in the `data` field of the response."""
		data = {}
		try:
			with open("{}/biocsnews.json".format(config.config["storage"]["news-path"]), "r") as file:
				data = json.load(file)
		except IOError as e:
			log.warning("Failed to load news file {}/biocsnews.json returning default response. Error: {}".format(config.config["storage"]["news-path"], e))
		return response("success", "Retrieve the BIO-CS News information success!", True, data=data), 200


class UpdateBioCSNews(Resource):
	@api.expect(news_parser)
	@api.response(200, "Updated news", response_wrapper)
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
		log.error("Failed to save bio/cs news update to {}: {}".format(config.config["storage"]["news-path"], e))
		return "Failed to save news update", 500
	return response("success", "Updated news", False)
