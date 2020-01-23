from datetime import datetime
from logging import getLogger

import sqlalchemy as sql
from flask_restplus import Resource, reqparse
from sqlalchemy import case, func, sql

from beecology_api.api import database
from beecology_api.api.cache import cache_response, invalidate_caches
from .authentication import authenticate, admin_required
from .utility import response

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
		engine = database.get_engine()
		bee = database.beerecord
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

		engine = database.get_engine()
		query = sql.update(database.beerecord).values(**args).where(database.beerecord.c.beerecord_id == id)
		results = engine.execute(query)

		if results.rowcount == 0:
			log.warning("Failed to update bee record #{}".format(id))
			return response("false", "Bee Dexes not found!", True), 404
		return response("success", "Retrieve the Bee information success!", False, data=[{"beerecord_id": id}]), 200

	@staticmethod
	@authenticate
	@invalidate_caches("beerecord")
	def delete(id: int, user):
		"""Delete a bee record by ID"""
		log.debug("Deleting bee record #{}".format(id))
		engine = database.get_engine()
		query = sql.delete(database.beerecord).where(database.beerecord.c.beerecord_id == id)
		results = engine.execute(query)

		if results.rowcount == 0:
			log.warning("Failed to delete bee record #{}".format(id))
			return response("false", "Bee record id not found!", True), 404
		return response("success", "Delete record success!", False, data=[{"beerecord_id": id}]), 200


class BeeRecordsList(Resource):
	@staticmethod
	@authenticate
	@admin_required
	def get(page: int, user=None):
		"""Get bee records by page"""
		log.debug("Getting page {} of bee records".format(page))
		engine = database.get_engine()
		bee = database.beerecord
		flower = database.flowerdict

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
		engine = database.get_engine()
		bee = database.beerecord
		flower = database.flowerdict
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
		engine = database.get_engine()

		bee = database.beerecord
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
		return response("success", "Retrieve all Bee Records", False, data=data), 200

class Beedex(Resource):
	@staticmethod
	@cache_response("beedict")
	def get(id: int = -1):
		"""Get an entry from the beedex by ID"""
		log.debug("Getting beedex entry #{}".format(id if id != -1 else "*"))
		engine = database.get_engine()
		query = sql.select([database.beedict])
		if id != -1:
			query = query.where(database.beedict.c.bee_id == id)
		results = engine.execute(query)

		data = [dict(r) for r in results]
		if len(data) == 0:
			log.warning("Failed to retrieve entry #{} from beedex".format(id))
			return response("false", "Bee Dexes not found!", True), 404
		log.debug("Returning {} beedex entries".format(len(data)))
		return response("success", "Retrieve the Bee information success!", False, data=data), 200

class NoElevationData(Resource):
	@staticmethod
	@cache_response("beerecord")
	def get():
		"""Get bee records for which there is no elevation info"""
		engine = database.get_engine()
		results = engine.execute(sql.select([database.beerecord]).where(database.beerecord.c.elevation.is_(None)))
		data = [dict(r) for r in results]
		if len(data) == 0:
			log.info("Failed to find bee records without elevations. This may be intended, depending on data quality.")
			return response("false", "No Elevation Records not found!", True), 404

		# Correct date format
		for datum in data:
			datum["time"] = datum["time"].strftime("%Y-%m-%dT%H:%M:%S.%fZ")
		return response("success", "Retrieve the No Elevation Records success!", False, data=data), 200

class RecordData(Resource):
	@staticmethod
	@authenticate
	def post(user):
		"""Record a new bee log"""
		parser = reqparse.RequestParser()
		parser.add_argument("chead", type=str, required=True, dest="coloration_head")
		parser.add_argument("cabdomen", type=str, required=True, dest="coloration_abdomen")
		parser.add_argument("cthorax", type=str, required=True, dest="coloration_thorax")
		parser.add_argument("gender", type=str, required=True)
		parser.add_argument("fname", type=str, required=True, dest="flower_name")
		parser.add_argument("cityname", type=str, required=True, dest="city_name"),
		parser.add_argument("fshape", type=str, required=True, dest="flower_shape")
		parser.add_argument("fcolor", type=str, required=True, dest="flower_color")
		parser.add_argument("beename", type=str, required=True, dest="bee_name"),
		parser.add_argument("loc", type=str, required=True, dest="loc_info")
		parser.add_argument("time", type=str, required=True, dest="time")
		parser.add_argument("recordpicpath", type=str, required=True, dest="record_pic_path")
		parser.add_argument("recordvideopath", type=str, required=False, dest="record_video_path")
		parser.add_argument("beedictid", type=str, required=False, dest="bee_dict_id")  # TODO revert to int type
		parser.add_argument("beebehavior", type=int, required=True, dest="bee_behavior")

		# Optional params that aren't specified in the v5 API but are in the bee web app API interface
		parser.add_argument("elevation", type=str, required=False)
		parser.add_argument("appversion", type=str, required=False, dest="app_version")

		args = parser.parse_args()

		# Terrible, terrible hack because the web app is broken and submits STRING DATES instead of beedictids
		# The old API didn't parse it correctly (i.e. throw a hissy fit because of an incorrect data type) and just
		# inserted the first number it could find in the date -- the year. This "workaround" makes this API mimic the
		# behavior of the old one. GOD @$%!ING DAMNIT I HATE MY LIFE
		# TODO UNFUCK BEEDICTID POSTING WHEN THE WEBAPP IS FIXED
		args["bee_dict_id"] = datetime.now().year

		log.info("User {} logging new bee record {}".format(user, args))

		# Convert time, bee_behavior
		try:
			args["time"] = datetime.strptime(args["time"], "%Y-%m-%dT%H:%M:%S.%fZ")
		except ValueError:
			return response("false", "Invalid date", True), 400

		if args["bee_behavior"] > 2 or args["bee_behavior"] < 0:
			return response("false", "Invalid beebehavior", True), 400
		args["bee_behavior"] = ["unknown", "nectar", "pollen"][args["bee_behavior"]]

		engine = database.get_engine()
		query = sql.insert(database.beerecord).values(**args, user_id=user)
		results = engine.execute(query)  # Not all SQL engines support RETURNING
		id = results.inserted_primary_key[0]

		if id is None:
			log.error("User {} failed to log new bee record {}".format(user, args))
			return response("false", "Log a new bee failed", True), 405
		return response("success", "Log a new bee success!", False, data=[{"beerecord_id": id}]), 200