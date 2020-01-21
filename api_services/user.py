import base64
import secrets
from datetime import datetime, timedelta
from logging import getLogger

from firebase_admin import auth
from flask import request
from flask_restplus import Resource
from sqlalchemy import sql, and_

from api_services import database
from .config import Config
from .authentication import authenticate
from .utility import response

log = getLogger()


class Enroll(Resource):
	@staticmethod
	def get():
		"""Enroll; uses a firebase token via basic auth to get a generate an access token"""
		if "Authorization" not in request.headers or request.headers["Authorization"].find("Basic") == -1:
			log.warning("User tried to enroll but didn't present a Firebase auth token")
			return response("false", "Firebase authorization token required", True), 403
		try:
			token = base64.standard_b64decode(request.headers["Authorization"].split(" ")[1])
			uid = auth.verify_id_token(token)["uid"]
		except Exception as e:
			log.warning("Firebase token failed validation: {}".format(e))
			return response("false", "Firebase token failed validation", True), 403

		# Generate token (1024 random bytes), expiration,
		accessToken = secrets.token_hex(1024)
		refreshToken = secrets.token_hex(1024)
		expiration = datetime.now() + timedelta(seconds=Config.config["auth"]["token-lifetime"])

		# Delete all other entries for this user and insert a new auth table entry. This effectively logs the user out
		# of all other devices, and helps keep the auth table clean.
		engine = database.get_engine()
		engine.execute(sql.delete(database.auth).where(database.auth.c.user_id == uid))
		engine.execute(sql.insert(database.auth).values(user_id=uid,
		                                                access_token=accessToken,
		                                                refresh_token=refreshToken,
		                                                token_expiry=expiration.timestamp() * 1000))
		log.debug("Enrolled user {}".format(uid))

		return {
			"accessToken": accessToken,
		    "refreshToken": refreshToken,
			"expiresIn": Config.config["auth"]["token-lifetime"] * 1000,
			"expiresAt": int(expiration.timestamp() * 1000),
			"type": "Bearer"
		}, 200


class Refresh(Resource):
	@staticmethod
	def get():
		"""Refresh a token"""
		if "Authorization" not in request.headers or request.headers["Authorization"].find("Bearer") == -1:
			return response("false", "Authorization required", True), 403
		try:
			decoded = base64.standard_b64decode(request.headers["Authorization"].split(" ")[1])
			refresh_token, firebase_token = decoded.decode("utf-8").split(":")
			uid = auth.verify_id_token(firebase_token)["uid"]
		except Exception as e:
			log.warning("Firebase token failed validation".format(e))
			return response("false", "Firebase token failed validation", True), 403

		# Verify we have an entry in the auth table corresponding to this uid+token combo
		engine = database.get_engine()
		results = engine.execute(sql.select([database.auth]).where(database.auth.c.user_id == uid
		                                                           and database.auth.c.refresh_token == refresh_token))
		if len([dict(r) for r in results]) == 0:
			log.warning("Failed to validate UID + refresh token for UID {}".format(uid))
			return response("false", "Failed to validate UID+refresh token", True), 403

		# Generate a new access token and expiration time, update them in the database
		access_token = secrets.token_hex(1024)
		expiration = datetime.now() + timedelta(seconds=Config.config["auth"]["token-lifetime"])

		engine.execute(sql.update(database.auth).values(token_expiry=expiration.timestamp() * 1000,
		                                                access_token=access_token) \
		               .where(and_(database.auth.c.refresh_token == refresh_token.decode("utf-8"), database.auth.c.user_id == uid)))

		return {
		       "accessToken": access_token,
		       "expiresIn": Config.config["auth"]["token-lifetime"] * 1000,
		       "expiresAt": int(expiration.timestamp() * 1000)
	    }, 200


class Unenroll(Resource):
	@staticmethod
	@authenticate
	def get(user):
		"""Remove access+refresh token from auth database"""
		engine = database.get_engine()
		engine.execute(sql.delete(database.auth).where(database.auth.c.user_id == user))
		return {"success", True}, 200
