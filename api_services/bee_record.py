from logging import getLogger

import sqlalchemy as sql
from flask_restplus import Resource, reqparse
from sqlalchemy import case, func

from api_services.authentication import authenticate
from api_services.utility import response
from api_services.cache import invalidate_caches, cache_response
from .database import Database

log = getLogger()

class BeeRecord(Resource):
	@staticmethod
	@authenticate
	@cache_response("beerecord")
	def get(id: int, user=None):
		"""Get a bee record by ID"""
		# Copied over from node server:
		# TODO Ask if we should scope it down to the specific user ID
		# TODO Any authenticated user can access any record ID
		log.debug("Getting bee record with ID")
		with Database() as engine:
			bee = Database.beerecord
			if id == -1:
				query = sql.select([bee.c.bee_dict_id, bee.c.bee_name, bee.c.loc_info, bee.c.time])
			else:
				query = sql.select([
					bee.c.beerecord_id,
					bee.c.user_id,
					bee.c.bee_dict_id,
					bee.c.bee_name,
					bee.c.coloration_head,
					bee.c.coloration_abdomen,
					bee.c.coloration_thorax,
					bee.c.gender,
					bee.c.flower_name,
					bee.c.city_name,
					bee.c.flower_shape,
					bee.c.flower_color,
					bee.c.loc_info,
					bee.c.time.label("date"),
					bee.c.bee_behavior,
					bee.c.record_pic_path,
					bee.c.record_video_path,
					bee.c.elevation
				]).where(bee.c.beerecord_id == id)
			
			results = engine.execute(query)
			data = [dict(r) for r in results]
			if len(data) == 0:
				log.warning("Failed to retrieve bee records for beerecord")
				return response("false", "Bee Records not found!", True), 404

			# Correct date format
			for datum in data:
				datum["date"] = datum["date"].strftime("%Y-%m-%dT%H:%M:%S.%fZ")
			return response("success", "Retrieve the Bee records success!", False, data=data), 200

	# TODO This should *probably* have auth...
	@staticmethod
	@invalidate_caches("beerecord")
	def put(id: int, user=None):
		"""Update a bee record by ID"""
		parser = reqparse.RequestParser()
		parser.add_argument("gender", type=str, required=False)
		parser.add_argument("fname", type=str, required=False, dest="flower_name")
		parser.add_argument("fcolor", type=str, required=False, dest="flower_color")
		parser.add_argument("beename", type=str, required=False, dest="bee_name")
		parser.add_argument("beebehavior", type=str, required=False, dest="bee_behavior")
		parser.add_argument("beedictid", type=int, required=False, dest="bee_dict_id")
		args = parser.parse_args()
		args = {k: v for k, v in args.items() if v is not None}  # Eliminate "None" args
		log.debug("Updating bee record {}".format(id))

		with Database() as engine:
			query = sql.update(Database.beerecord).values(**args).where(Database.beerecord.c.beerecord_id == id)\
				.returning(Database.beerecord.c.beerecord_id)
			results = engine.execute(query)
			id = [dict(r) for r in results]
			if len(id) == 0:
				log.warning("Failed to update bee record #{}".format(id))
				return response("false", "Bee Dexes not found!", True), 404
			return response("success", "Retrieve the Bee information success!", False, data=id), 200

	@staticmethod
	@authenticate
	@invalidate_caches("beerecord")
	def delete(id: int, user):
		"""Delete a bee record by ID"""
		log.debug("Deleting bee record #{}".format(id))
		with Database() as engine:
			query = sql.delete(Database.beerecord).where(Database.beerecord.c.beerecord_id == id)\
				.returning(Database.beerecord.c.beerecord_id)
			results = engine.execute(query)
			data = [dict(r) for r in results]
			if len(data) == 0:
				log.warning("Failed to delete bee record #{}".format(id))
				return response("false", "Bee record id not found!", True), 404
			return response("success", "Delete record success!", False, data=data), 200

class BeeRecordsList(Resource):
	@staticmethod
	@cache_response("beerecord", "flowerdict")
	def get(page: int):
		"""Get bee records by page"""
		log.debug("Getting page {} of bee records".format(page))
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
				log.error("Failed to retrieve bee records for beerecords")
				return response("false", "Bee records not found!", True), 404

			# Correct date format
			for datum in data:
				datum["time"] = datum["time"].strftime("%Y-%m-%dT%H:%M:%S.%fZ")
			return response("success", "Retrieve the Bee records success!", False, data=data), 200

class BeeVisRecords(Resource):
	@staticmethod
	@cache_response("beerecord", "flowerdict")
	def get():
		"""Get all bee records"""
		log.debug("Getting all bee records")
		with Database() as engine:
			bee = Database.beerecord
			flower = Database.flowerdict
			# TODO Remove duplicate gender entry (requires modifications to sites that rely on this endpoint)
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
				log.error("Failed to retrieve bee records for beevisrecords")
				return response("false", "Bee records not found!", True), 404

			# Correct date format
			for datum in data:
				datum["date"] = datum["date"].strftime("%Y-%m-%dT%H:%M:%S.%fZ")

			return response("success", "Retrieve the Bee records success!", False, data=data), 200

class BeeUserRecords(Resource):
	@staticmethod
	@authenticate
	def get(user):
		"""Get bee log records by user ID"""
		log.debug("Getting all bee records for user {}".format(user))
		with Database() as engine:
			bee = Database.beerecord
			query = sql.select([
				bee.c.beerecord_id,
				bee.c.user_id,
				bee.c.bee_behavior,
				bee.c.bee_dict_id,
				bee.c.bee_name,
				bee.c.coloration_head,
				bee.c.coloration_abdomen,
				bee.c.coloration_thorax,
				bee.c.gender,
				bee.c.flower_name,
				bee.c.city_name,
				bee.c.flower_shape,
				bee.c.flower_color,
				bee.c.loc_info,
				bee.c.time.label("date"),
				bee.c.record_pic_path,
				bee.c.record_video_path
			]).where(bee.c.user_id == user)

			results = engine.execute(query)
			data = [dict(r) for r in results]
			if len(data) == 0:
				log.warning("Failed to retrieve bee records for user {}".format(user))
				return response("false", "Bee Records not found!", True), 404

			# Correct date format
			for datum in data:
				datum["date"] = datum["date"].strftime("%Y-%m-%dT%H:%M:%S.%fZ")
			return response("success", "Retrieve all bee records", False, data=data), 200

class Beedex(Resource):
	@staticmethod
	@cache_response("beedict")
	def get(id: int = -1):
		"""Get an entry from the beedex by ID"""
		log.debug("Getting beedex entry #{}".format(id if id != -1 else "*"))
		with Database() as engine:
			query = sql.select([Database.beedict])
			if id != -1:
				query = query.where(Database.beedict.c.bee_id == id)
			results = engine.execute(query)

			data = [dict(r) for r in results]
			if len(data) == 0:
				log.warning("Failed to retrieve entry #{} from beedex".format(id))
				return response("false", "Bee Dexes not found!", True), 404
			log.debug("Returning {} beedex entries".format(len(data)))
			return response("success", "Retrieve the Bee information success!", False, data=data), 200
