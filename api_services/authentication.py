import base64
from logging import getLogger

from firebase_admin import auth
from flask import request
from sqlalchemy import sql, and_

from api_services import database
from .config import Config
from api_services.utility import response

log = getLogger()

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
