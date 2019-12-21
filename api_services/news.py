import json
from logging import getLogger

from flask_restplus import Resource, reqparse

from api_services.utility import response
from .config import Config

log = getLogger()

class News(Resource):
	@staticmethod
	def get():
		try:
			with open("{}/news.json".format(Config.config["news"]["folder"]), "r") as file:
				return response("success", "Retrieve the News information success!", True, data=json.load(file))
		except IOError as e:
			log.error("Failed to load news file {}/news.json: {}".format(Config.config["news"]["folder"], e))
			return response("false", "Failed to load news file", True), 500

	@staticmethod
	def put():
		parser = reqparse.RequestParser()
		parser.add_argument("code", type=str, required=True)
		parser.add_argument("json", type=dict, required=True)
		args = parser.parse_args()

		return update_news_file(args["code"], args["json"], "news.json")

class BioCSNews(Resource):
	@staticmethod
	def get():
		try:
			with open("{}/biocsnews.json".format(Config.config["news"]["folder"]), "r") as file:
				return response("success", "Retrieve the BIO-CS News information success!", True, data=json.load(file))
		except IOError as e:
			log.error("Failed to load news file {}/biocsnews.json: {}".format(Config.config["news"]["folder"], e))
			return response("false", "Failed to load news file", True), 500

	@staticmethod
	def put():
		"""Update Bio/CS news"""
		parser = reqparse.RequestParser()
		parser.add_argument("code", type=str, required=True)
		parser.add_argument("json", type=dict, required=True)
		args = parser.parse_args()

		return update_news_file(args["code"], args["json"], "biocsnews.json")


def update_news_file(code, news, filename):
	if code != Config.config["news"]["update-code"]:
		return "Incorrect update code", 403
	try:
		with open("{}/{}".format(Config.config["news"]["folder"], filename), "w") as file:
			json.dump(news, file)
	except IOError as e:
		log.error("Failed to save bio/cs news update to {}: {}".format(Config.config["news"]["folder"], e))
		return "Failed to save news update", 500
	return response("success", "Updated news", False)
