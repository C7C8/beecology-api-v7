import base64
import secrets
from datetime import datetime, timedelta
from logging import getLogger

from firebase_admin import auth
from flask import request
from flask_restx import Resource
from sqlalchemy import sql, and_

from beecology_api import database
from beecology_api import config
from beecology_api.compat_bee_api.api import api
from beecology_api.compat_bee_api.authentication import authenticate
from beecology_api.compat_bee_api.models import response_wrapper, user_token_pair, user_access_token
from beecology_api.compat_bee_api.response import response

log = getLogger()


class Enroll(Resource):
	@api.doc(security="firebase")
	@api.response(403, "Firebase authorization token not present or failed validation", response_wrapper)
	@api.response(200, "Succeeded authentication, user token pair enclosed", user_token_pair)
	def get(self):
		"""Enroll; uses a firebase token via basic auth to get a generate an access token.

		Enrolling will result in removal of all other enrollments from the authentication database, i.e. all other
		sessions for this user are automatically logged out."""
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
		expiration = datetime.now() + timedelta(seconds=config.config["auth"]["token-lifetime"])

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
			"expiresIn": config.config["auth"]["token-lifetime"] * 1000,
			"expiresAt": int(expiration.timestamp() * 1000),
			"type": "Bearer"
		}, 200


class Refresh(Resource):
	@api.param("Authorization", "User's refresh token as HTTP bearer token authorization", _in="header", required=True)
	@api.response(403, "Firebase authorization token not present or failed validation", response_wrapper)
	@api.response(200, "Refreshed access token enclosed", user_access_token)
	def get(self):
		"""Obtain a new access token using a refresh token."""
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
		expiration = datetime.now() + timedelta(seconds=config.config["auth"]["token-lifetime"])

		engine.execute(sql.update(database.auth).values(token_expiry=expiration.timestamp() * 1000,
		                                                access_token=access_token) \
		               .where(and_(database.auth.c.refresh_token == refresh_token.decode("utf-8"), database.auth.c.user_id == uid)))

		return {
		       "accessToken": access_token,
		       "expiresIn": config.config["auth"]["token-lifetime"] * 1000,
		       "expiresAt": int(expiration.timestamp() * 1000)
	    }, 200


class Unenroll(Resource):
	@api.response("200", "Removed user from database")
	@authenticate
	def get(self, user):
		"""Remove access+refresh token from the authentication database"""
		engine = database.get_engine()
		engine.execute(sql.delete(database.auth).where(database.auth.c.user_id == user))
		return {"success": True}, 200
