from datetime import datetime
from logging import getLogger

from flask_restplus import Resource, reqparse
from sqlalchemy import sql

from api_services.auth import authenticate
from api_services.database import Database
from api_services.util import response

log = getLogger()

class RecordData(Resource):
	@staticmethod
	@authenticate
	def post(user=None):
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
		parser.add_argument("time", type=datetime, required=True, dest="time")
		parser.add_argument("recordpicpath", type=str, required=True, dest="record_pic_path")
		parser.add_argument("recordvideopath", type=str, required=True, dest="record_video_path")
		parser.add_argument("beedictid", type=str, required=False, dest="bee_dict_id")
		parser.add_argument("beebehavior", type=str, required=True, dest="bee_behavior")
		args = parser.parse_args()
		log.info("User {} logging new bee record {}".format(user, args))

		# Validate bee_dict_id, convert bee_behavior
		if "bee_dict_id" not in args:
			args["bee_dict_id"] = -1
		try:
			behavior = int(args["bee_behavior"])  # Will throw ValueError if not a string
			if behavior > 2 or behavior < 0:
				raise ValueError
		except ValueError:
			return response("false", "Invalid beebehavior", True), 400
		args["bee_behavior"] = ["unknown", "nectar", "pollen"][behavior]

		with Database() as engine:
			query = sql.insert(Database.beerecord).values(**args).returning(Database.beerecord.c.beerecord_id)
			results = engine.execute(query)
			result = engine.execute(query)
			id = dict(next(result))

			if len(id) == 0:
				log.error("User {} failed to log new bee record {}".format(user, args))
				return response("false", "Log a new bee failed", True), 405
			return response("success", "Log a new bee success!", False, data=id), 200


class Enroll(Resource):
	@staticmethod
	def get():
		"""Register"""
		return "Placeholder"

class Refresh(Resource):
	@staticmethod
	def get():
		"""Login"""
		return "Placeholder"

class Unenroll(Resource):
	@staticmethod
	def get():
		"""Deregister (delete login)"""
		return "Placeholder"
