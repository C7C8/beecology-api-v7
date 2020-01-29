from datetime import datetime
from logging import getLogger

import sqlalchemy as sql
from flask_restx import Resource
from sqlalchemy import case, func, sql

from beecology_api import database
from beecology_api.bee_data_api.api import api
from beecology_api.bee_data_api.authentication import authenticate, admin_required
from beecology_api.bee_data_api.cache import cache_response, invalidate_caches
from beecology_api.bee_data_api.models import bee_record_update_parser, response_wrapper, bee_record_response, \
	bee_record_by_page_response, bee_vis_record_response, bee_record_no_elevation_response, beedex_response, \
	bee_record_parser
from beecology_api.bee_data_api.response import response

log = getLogger()


class BeeRecord(Resource):
	@api.response(200, "Success", bee_record_response)
	@api.response(404, "Bee record not found", response_wrapper)
	@authenticate
	@cache_response("beerecord")
	def get(self, id: int, user=None):
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
			return response("false", "Bee Records not found!", True), 200

		# Correct date format
		for datum in data:
			datum["date"] = datum["date"].strftime("%Y-%m-%dT%H:%M:%S.%fZ")
		return response("success", "Retrieve the Bee records success!", False, data=data), 200

	# TODO This should *probably* have auth...
	@api.response(200, "Update succeeded", response_wrapper)
	@api.response(404, "Bee record not found", response_wrapper)
	@api.expect(bee_record_update_parser)
	@invalidate_caches("beerecord")
	def put(self, id: int, user=None):
		"""Update a bee record by ID"""
		args = bee_record_update_parser.parse_args()
		args = {k: v for k, v in args.items() if v is not None}  # Eliminate "None" args
		log.debug("Updating bee record {}".format(id))

		engine = database.get_engine()
		query = sql.update(database.beerecord).values(**args).where(database.beerecord.c.beerecord_id == id)
		results = engine.execute(query)

		if results.rowcount == 0:
			log.warning("Failed to update bee record #{}".format(id))
			return response("false", "Bee Dexes not found!", True), 200
		return response("success", "Retrieve the Bee information success!", False, data=[{"beerecord_id": id}]), 200

	@api.response(200, "Bee record deleted successfully", response_wrapper)
	@api.response(404, "Failed to find bee record", response_wrapper)
	@authenticate
	@invalidate_caches("beerecord")
	def delete(self, id: int, user):
		"""Delete a bee record by ID"""
		log.debug("Deleting bee record #{}".format(id))
		engine = database.get_engine()
		query = sql.delete(database.beerecord).where(database.beerecord.c.beerecord_id == id)
		results = engine.execute(query)

		if results.rowcount == 0:
			log.warning("Failed to delete bee record #{}".format(id))
			return response("false", "Bee record id not found!", True), 200
		return response("success", "Delete record success!", False, data=[{"beerecord_id": id}]), 200


class BeeRecordsList(Resource):
	@api.response(200, "Found bee records", bee_record_by_page_response)
	@api.response(404, "Failed to find bee records", response_wrapper)
	@admin_required
	def get(self, page: int, user=None):
		"""Get bee records by page (segments of 50). Requires administrator access."""
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
			return response("false", "Bee records not found!", True), 200

		# Correct date format
		for datum in data:
			datum["time"] = datum["time"].strftime("%Y-%m-%dT%H:%M:%S.%fZ")
		return response("success", "Retrieve the Bee records success!", False, data=data), 200


class BeeVisRecords(Resource):
	@api.response(200, "Found bee records", bee_vis_record_response)
	@api.response(404, "Failed to find bee records", response_wrapper)
	@cache_response("beerecord", "flowerdict")
	def get(self):
		"""Get all bee records (reduced).

		**Warning!** This returns an *extremely* large dataset, literally the entire contents of the database!
		Historically this endpoint has responded with several *mega*bytes of data, so bee **careful!**
		"""
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
			return response("false", "Bee records not found!", True), 200

		# Correct date format
		for datum in data:
			datum["date"] = datum["date"].strftime("%Y-%m-%dT%H:%M:%S.%fZ")

		return response("success", "Retrieve the Bee records success!", False, data=data), 200


class BeeUserRecords(Resource):
	@api.response(200, "Retrieved bee records for user", bee_record_no_elevation_response)
	@api.response(404, "Failed to retrieve records for user", response_wrapper)
	@authenticate
	def get(self, user):
		"""Get all bee logs for a user. Supplying the user ID is not required, it's extracted from the authorization token."""
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
			return response("false", "Bee Records not found!", True), 200

		# Correct date format
		for datum in data:
			datum["date"] = datum["date"].strftime("%Y-%m-%dT%H:%M:%S.%fZ")
		return response("success", "Retrieve all Bee Records", False, data=data), 200

class Beedex(Resource):
	@staticmethod
	@api.response(200, "Retrieved BeeDex entry", beedex_response)
	@api.response(404, "Failed to retrieve BeeDex entry", response_wrapper)
	@cache_response("beedict")
	def get(id: int = -1):
		"""Get an entry from the beedex by ID. If no ID is provided, all beedex entries are returned."""
		log.debug("Getting beedex entry #{}".format(id if id != -1 else "*"))
		engine = database.get_engine()
		query = sql.select([database.beedict])
		if id != -1:
			query = query.where(database.beedict.c.bee_id == id)
		results = engine.execute(query)

		data = [dict(r) for r in results]
		if len(data) == 0:
			log.warning("Failed to retrieve entry #{} from beedex".format(id))
			return response("false", "Bee Dexes not found!", True), 200
		log.debug("Returning {} beedex entries".format(len(data)))
		return response("success", "Retrieve the Bee information success!", False, data=data), 200

class NoElevationData(Resource):
	@api.response(200, "Retrieved bee records", bee_record_by_page_response)
	@api.response(404, "Failed to retrieve bee records", response_wrapper)
	@cache_response("beerecord")
	def get(self):
		"""Get bee records for which there is no elevation info"""
		engine = database.get_engine()
		results = engine.execute(sql.select([database.beerecord]).where(database.beerecord.c.elevation.is_(None)))
		data = [dict(r) for r in results]
		if len(data) == 0:
			log.info("Failed to find bee records without elevations. This may be intended, depending on data quality.")
			return response("false", "No Elevation Records not found!", True), 200

		# Correct date format
		for datum in data:
			datum["time"] = datum["time"].strftime("%Y-%m-%dT%H:%M:%S.%fZ")
		return response("success", "Retrieve the No Elevation Records success!", False, data=data), 200

class RecordData(Resource):
	@api.expect(bee_record_parser)
	@api.response(200, "Successfully logged new bee record", response_wrapper)
	@api.response(400, "Invalid date or bee behavior", response_wrapper)
	@authenticate
	def post(self, user):
		"""Record a new bee log. Requires user login."""

		# Optional params that aren't specified in the v5 API but are in the bee web app API interface
		args = bee_record_parser.parse_args()

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

		# TODO re-implement proper ID returning
		# if id is None:
		# 	log.error("User {} failed to log new bee record {}".format(user, args))
		# 	return response("false", "Log a new bee failed", True), 405
		return response("success", "Log a new bee success!", False, data=[{"beerecord_id": 5}]), 200
