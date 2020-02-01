import base64
from logging import getLogger
from functools import wraps

from firebase_admin import auth
from flask import request
from sqlalchemy import sql, and_

from beecology_api import config
from beecology_api import database
from beecology_api.compat_bee_api.api import api
from beecology_api.compat_bee_api.models import response_wrapper
from beecology_api.compat_bee_api.response import response

log = getLogger()

# TODO Clean this up a bit

authParser = api.parser()
authParser.add_argument("Authorization", location="headers", help="Bearer token authorization")

def authenticate(func):
	"""Decorator for user authentication"""
	@wraps(func)
	@api.response(403, "Authorization failed", response_wrapper)
	@api.doc(security="user")
	def wrapper(*args, **kwargs):
		# Allow unit tests to skip authentication
		if "testing" in config.config and config.config["testing"]:
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


adminParser = api.parser()

def admin_required(func):
	"""Decorator for requiring administrator access"""
	@wraps(func)
	@api.response(403, "Administrator access required")
	@api.doc(security="admin")
	@authenticate
	def admin_wrapper(*args, **kwargs):
		# Allow unit tests to skip admin guards
		if "testing" in config.config and config.config["testing"]:
			return func(*args, **kwargs)

		# Check administrator table to see if there's an entry for this user. If there isn't, return an error.
		engine = database.get_engine()
		results = engine.execute(sql.select([database.admin]).where(database.admin.c.user_id == kwargs["user"]))
		if len(next(results, {})) == 0:
			return response("false", "Administrator access required", True), 403

		log.debug("Authenticated admin \"{}\"".format(kwargs["user"]))
		return func(*args, **kwargs)
	return admin_wrapper
