from logging import getLogger

from flask_restplus import Resource

from api_services.util import response
from .database import DatabaseService

log = getLogger()

class BeeRecord(Resource):
	@staticmethod
	def get():
		"""Get a bee record by ID"""
		return "Placeholder"

	@staticmethod
	def put():
		"""Update a bee record by ID"""
		return "Placeholder"

	@staticmethod
	def delete():
		"""Delete a bee record by ID"""
		return "Placeholder"

class BeeRecordsList(Resource):
	@staticmethod
	def get():
		"""Get bee records by page"""
		return "Placeholder"

class BeeVisRecords(Resource):
	@staticmethod
	def get():
		"""Get all bee records"""
		return "Placeholder"

class BeeUserRecords(Resource):
	@staticmethod
	def get():
		"""Get bee log records by user ID"""
		return "Placeholder"

class Beedex(Resource):
	@staticmethod
	def get(id=-1):
		"""Get an entry from the beedex by ID"""
		log.info("Getting beedex ID {}".format(id if id != -1 else "*"))
		with DatabaseService() as cursor:
			cursor.execute("SELECT * FROM beedict " + ("WHERE bee_id=%s" if id != -1 else ""), [id])
			results = cursor.fetchall()
			if len(results) == 0:
				return response("false", "Bee Dexes not found!", True), 404
			data = [{
					"bee_id": result[0],
					"bee_name": result[1],
					"common_name": result[2],
					"description": result[3],
					"active_months": result[4],
					"confused": result[5],
					"bee_pic_path": result[6],
					"abdomen_list": result[7],
					"thorax_list": result[8],
					"head_list": result[9]
				} for result in results]
			log.info("Returning {} beedex entries".format(len(data)))
			return response("success", "Retrieve the Bee information success!", False, data=data), 200

