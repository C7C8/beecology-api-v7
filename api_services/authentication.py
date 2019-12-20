import base64
from logging import getLogger

from firebase_admin import auth
from flask import request
from sqlalchemy import sql, and_

from api_services.database import Database
from api_services.utility import response

log = getLogger()

def authenticate(func):
	"""Decorator for user authentication"""
	def wrapper(*args, **kwargs):
		if "Authorization" not in request.headers:
			return response("false", "Authorization required", True), 403
		try:
			decoded = base64.standard_b64decode(request.headers["Authorization"].split(" ")[1]).decode("utf-8")
			firebase_token, access_token = decoded.split(":")
			uid = auth.verify_id_token(access_token)["uid"]
		except Exception as e:
			log.info("User failed authentication: {}".format(e))
			return response("false", "Failed to authenticate: {}".format(e), True), 403

		with Database() as engine:
			query = sql.select([Database.auth]).where(and_(Database.auth.c.user_id == uid,
			                                               Database.auth.c.access_token == access_token))
			results = engine.execute(query)
			if len(next(results, {})) == 0:
				return response("false", "Authorization failed, please enroll first", True), 403

		log.info("Authenticated user \"{}\"".format(uid))
		return func(*args, **kwargs, user=uid)

	return wrapper
