from logging import getLogger

import sqlalchemy as sql
from flask_restplus import Resource
from sqlalchemy import case, func

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
	def get(page: int):
		"""Get bee records by page"""
		with Database() as engine:
			bee = Database.beerecord
			flower = Database.flowerdict
			query = sql.select([
				bee.c.beerecord_id,
				bee.c.bee_dict_id,
				bee.c.bee_name,
				bee.c.coloration_abdomen,
				bee.c.coloration_thorax,
				bee.c.coloration_head,
				flower.c.shape.label("flower_shape"),
				flower.c.colors.label("flower_color"),
				bee.c.time,
				bee.c.loc_info,
				bee.c.user_id,
				bee.c.record_pic_path,
				bee.c.record_video_path,
				bee.c.flower_name,
				bee.c.city_name,
				bee.c.gender,
				bee.c.bee_behavior,
				flower.c.common_name,
				bee.c.app_version,
				bee.c.elevation
			]).select_from(
				bee.join(flower, bee.c.flower_name == flower.c.latin_name, isouter=True)
			).where(
				bee.c.user_id != "ecpierce@wpi.edu" and
				bee.c.user_id != "historical@edu.com"
			).order_by(bee.c.beerecord_id.desc()).limit(50).offset(50*(page - 1))

			results = engine.execute(query)
			data = [dict(r) for r in results]
			if len(data) == 0:
				return response("false", "Bee records not found!", True), 404

			# Correct date format
			for datum in data:
				datum["time"] = datum["time"].strftime("%Y-%m-%dT%H:%M:%S.%fZ")
			return response("success", "Retrieve the Bee records success!", False, data=data), 200

class BeeVisRecords(Resource):
	@staticmethod
	def get():
		"""Get all bee records"""
		# TODO Cache responses from this endpoint
		with Database() as engine:
			bee = Database.beerecord
			flower = Database.flowerdict
			# TODO Remove duplicate gender entry (requires external code modifications)
			query = sql.select([
				bee.c.bee_name,
				bee.c.time.label("date"),
				bee.c.loc_info,
				bee.c.elevation,
				flower.c.shape.label("flower_shape"),
				flower.c.main_common_name.label("flower_name"),
				flower.c.main_color.label("flower_color"),
				bee.c.bee_behavior,
				bee.c.gender.label("spgender"),
				case([
					(func.lower(bee.c.gender) == "queen" or func.lower(bee.c.gender) == "worker" or func.lower(bee.c.gender) == "female", "Female"),
					(func.lower(bee.c.gender) == "male", "Male"),
					(func.lower(bee.c.gender) == "male/female", "unknown"),
					(func.lower(bee.c.gender) == "unknown", "unknown")
				], else_=bee.c.gender).label("gender")
			]).select_from(bee.join(flower, flower.c.latin_name == bee.c.flower_name))
			results = engine.execute(query)

			data = [dict(r) for r in results]
			if len(data) == 0:
				return response("false", "Bee records not found!", True), 404

			# Correct date format, gender format (yes, there's a duplicate, but this API conforms to the original)
			for datum in data:
				datum["date"] = datum["date"].strftime("%Y-%m-%dT%H:%M:%S.%fZ")

			return response("success", "Retrieve the Bee records success!", False, data=data), 200

class BeeUserRecords(Resource):
	@staticmethod
	def get():
		"""Get bee log records by user ID"""
		return "Placeholder"

class Beedex(Resource):
	@staticmethod
	def get(id: int = -1):
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

