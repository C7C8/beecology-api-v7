from logging import getLogger
import sqlalchemy as sql

from flask_restplus import Resource

from api_services.util import response
from .database import Database

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
		with Database() as engine:
			query = sql.select([Database.beedict])
			if id != -1:
				query = query.where(Database.beedict.c.bee_id == id)
			results = engine.execute(query)

			data = [dict(r) for r in results]
			if len(data) == 0:
				return response("false", "Bee Dexes not found!", True), 404
			log.info("Returning {} beedex entries".format(len(data)))
			return response("success", "Retrieve the Bee information success!", False, data=data), 200

