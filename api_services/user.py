import base64
import secrets
from datetime import datetime, timedelta
from logging import getLogger

from firebase_admin import auth
from flask import request
from flask_restplus import Resource, reqparse
from sqlalchemy import sql

from .config import Config
from api_services.authentication import authenticate
from api_services.database import Database
from api_services.utility import response

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
		parser.add_argument("time", type=str, required=True, dest="time")
		parser.add_argument("recordpicpath", type=str, required=True, dest="record_pic_path")
		parser.add_argument("recordvideopath", type=str, required=False, dest="record_video_path")
		parser.add_argument("beedictid", type=int, required=False, dest="bee_dict_id")
		parser.add_argument("beebehavior", type=int, required=True, dest="bee_behavior")

		# Optional params that aren't specified in the v5 API but are in the bee web app API interface
		parser.add_argument("elevation", type=str, required=False)
		parser.add_argument("appversion", type=str, required=False, dest="app_version")

		args = parser.parse_args()
		log.info("User {} logging new bee record {}".format(user, args))

		# Convert time, bee_behavior
		try:
			args["time"] = datetime.strptime(args["time"], "%Y-%m-%dT%H:%M:%S.%fZ")
		except ValueError:
			return response("false", "Invalid date", True), 400

		if args["bee_behavior"] > 2 or args["bee_behavior"] < 0:
			return response("false", "Invalid beebehavior", True), 400
		args["bee_behavior"] = ["unknown", "nectar", "pollen"][args["bee_behavior"]]

		with Database() as engine:
			query = sql.insert(Database.beerecord).values(**args).returning(Database.beerecord.c.beerecord_id)
			results = engine.execute(query)
			id = [dict(r) for r in results]

			if len(id) == 0:
				log.error("User {} failed to log new bee record {}".format(user, args))
				return response("false", "Log a new bee failed", True), 405
			return response("success", "Log a new bee success!", False, data=id), 200


class Enroll(Resource):
	@staticmethod
	def get():
		"""Enroll; uses a firebase token via basic auth to get a generate an access token"""
		if "Authorization" not in request.headers or request.headers["Authorization"].find("Basic") == -1:
			return response("false", "Firebase authorization token required", True), 403
		token = base64.standard_b64decode(request.headers["authorization"].split(" ")[1])
		try:
			uid = auth.verify_id_token(token)["uid"]
		except Exception as e:
			log.error("Firebase token {} failed validation: {}".format(token, e))
			return response("false", "Firebase token failed validation", True), 403

		# Generate token (1024 random bytes), expiration,
		accessToken = secrets.token_hex(1024)
		refreshToken = secrets.token_hex(1024)
		expiration = datetime.now() + timedelta(seconds=Config.config["auth"]["token-expiration"])

		# Delete all other entries for this user and insert a new auth table entry. This effectively logs the user out
		# of all other devices, and helps keep the auth table clean.
		with Database() as engine:
			engine.execute(sql.delete(Database.auth).where(Database.auth.c.user_id == uid))
			engine.execute(sql.insert(Database.auth).values(user_id=uid,
			                                                access_token=accessToken,
			                                                refresh_token=refreshToken,
			                                                token_expiry=expiration.timestamp() * 1000))
		log.info("Enrolled user {}".format(uid))

		return {
			"accessToken": accessToken,
			"refreshToken": refreshToken,
			"expiresIn": Config.config["auth"]["token-expiration"] * 1000,
			"expiresAt": int(expiration.timestamp() * 1000),
			"type": "Bearer"
		}, 200

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
