import base64
from logging import getLogger

from firebase_admin import auth
from flask import request
from sqlalchemy import sql, and_

from api_services import database
from .config import Config
from .utility import response

log = getLogger()

# TODO Clean this up a bit


def authenticate(func):
	"""Decorator for user authentication"""
	def wrapper(*args, **kwargs):
		# Allow unit tests to skip authentication
		if "testing" in Config.config and Config.config["testing"]:
			return func(*args, **kwargs, user="UNIT TEST")

		if "Authorization" not in request.headers:
			return response("false", "Authorization required", True), 403
		try:
			decoded = base64.standard_b64decode(request.headers["Authorization"].split(" ")[1]).decode("utf-8")
			access_token, firebase_token = decoded.split(":")
			uid = auth.verify_id_token(firebase_token)["uid"]
		except Exception as e:
			log.info("User failed authentication: {}".format(e))
			return response("false", "Failed to authenticate: {}".format(e), True), 403

		engine = database.get_engine()
		query = sql.select([database.auth]).where(and_(database.auth.c.user_id == uid,
		                                               database.auth.c.access_token == access_token))
		results = engine.execute(query)
		if len(next(results, {})) == 0:
			return response("false", "Authorization failed, please enroll first", True), 403

		log.debug("Authenticated user \"{}\"".format(uid))
		return func(*args, **kwargs, user=uid)
	return wrapper


def admin_required(func):
	"""Decorator for requiring administrator access. IMPORTANT: This must come AFTER a user authentication check"""
	def admin_wrapper(*args, **kwargs):
		# Allow unit tests to skip admin guards
		if "testing" in Config.config and Config.config["testing"]:
			return func(*args, **kwargs)

		if "user" not in kwargs:
			return response("false", "Login required", True), 403

		# Check administrator table to see if there's an entry for this user. If there isn't, return an error.
		engine = database.get_engine()
		results = engine.execute(sql.select([database.admin]).where(database.admin.c.user_id == kwargs["user"]))
		if len(next(results, {})) == 0:
			return response("false", "Administrator access required", True), 403

		log.debug("Authenticated admin \"{}\"".format(kwargs["user"]))
		return func(*args, **kwargs)
	return admin_wrapper
