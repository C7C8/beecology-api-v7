from logging import getLogger

import sqlalchemy as sql
from flask import jsonify
from flask_restplus import Resource
from sqlalchemy import Date, case, func

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
		# TODO Cache responses from this endpoint
		with Database() as engine:
			beerecord = Database.beerecord
			flowerdict = Database.flowerdict
			# TODO Remove duplicate gender entry (requires external code modifications)
			query = sql.select([
				beerecord.c.bee_name,
				beerecord.c.time.label("date"),
				beerecord.c.loc_info,
				beerecord.c.elevation,
				flowerdict.c.shape.label("flower_shape"),
				flowerdict.c.main_common_name.label("flower_name"),
				flowerdict.c.main_color.label("flower_color"),
				beerecord.c.bee_behavior,
				beerecord.c.gender.label("spgender"),
				case([
					(func.lower(beerecord.c.gender) == "queen" or func.lower(beerecord.c.gender) == "worker" or func.lower(beerecord.c.gender) == "female", "Female"),
					(func.lower(beerecord.c.gender) == "male", "Male"),
					(func.lower(beerecord.c.gender) == "male/female", "unknown"),
					(func.lower(beerecord.c.gender) == "unknown", "unknown")
				], else_=beerecord.c.gender).label("gender")
			]).select_from(beerecord.join(flowerdict, flowerdict.c.latin_name == beerecord.c.flower_name))
			results = engine.execute(query)

			# Correct date format, gender format (yes, there's a duplicate, but this API conforms to the original)
			data = [dict(r) for r in results]
			for datum in data:
				datum["date"] = datum["date"].strftime("%Y-%m-%dT%H:%M:%S.%fZ")

			if len(data) == 0:
				return response("false", "Bee records not found!", True), 404
			return response("success", "Retrieve the Bee records success!", False, data=data), 200

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

