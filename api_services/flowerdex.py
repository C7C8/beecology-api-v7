from logging import getLogger

from flask_restplus import Resource

from api_services.database import DatabaseService
from api_services.util import response

log = getLogger()

class Flowerdex(Resource):
	@staticmethod
	def get(id: int = -1):
		"""Get flower by ID"""
		log.info("Getting flowerdex ID {}".format(id if id != -1 else "*"))
		with DatabaseService() as cursor:
			cursor.execute("SELECT * FROM flowerdict " + ("WHERE flower_id=%s" if id != -1 else ""), [id])
			results = cursor.fetchall()
			if len(results) == 0:
				return response("false", "Flower not found!", True), 404

			data = [{
				"flower_id": result[0],
				"flower_latin_name": result[1],
				"flower_common_name": result[2]
			} for result in results]
			log.info("Returning {} flowerdex entries".format(len(data)))
			return response("success", "Retrieve the Flower information success!", False, data=data), 200

	@staticmethod
	def post():
		"""Create a new flower"""
		return "Placeholder"

	@staticmethod
	def put():
		"""Update a flower by ID"""
		return "Placeholder"

	@staticmethod
	def delete():
		"""Delete flower by ID"""
		return "Placeholder"

class FlowerShapes(Resource):
	@staticmethod
	def get():
		"""Get all flower shapes"""
		return "Placeholder"

class FlowerColors(Resource):
	@staticmethod
	def get():
		"""Get all flower colors"""
		return "Placeholder"

class UnmatchedFlowers(Resource):
	@staticmethod
	def get():
		"""Get unmatched flowers"""
		return "Placeholder"
