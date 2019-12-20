import base64
from logging import getLogger

from firebase_admin import auth
from flask import request

from api_services.utility import response

log = getLogger()

def authenticate(func):
	"""Decorator for user authentication"""
	def wrapper(*args, **kwargs):
		if "Authorization" not in request.headers:
			return response("false", "Authorization required", True), 401
		decoded = base64.standard_b64decode(request.headers["Authorization"].split(" ")[1]).decode("utf-8")
		tokens = decoded.split(":")
		try:
			uid = auth.verify_id_token(tokens[1])["uid"]
		except Exception as e:
			log.info("User ID {} failed authentication: ".format(tokens[0], e))
			return response("false", "Failed to authenticate: {}".format(e), True), 403

		log.info("Authenticated user \"{}\"".format(uid))
		return func(*args, **kwargs, user=uid)

	return wrapper
