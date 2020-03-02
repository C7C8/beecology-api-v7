from functools import wraps

from flask_jwt_extended import verify_jwt_in_request, get_jwt_claims
from flask_restx import abort


def authenticate(api):
	"""Decorator for requiring authentication, but it attaches Swagger docs to the endpoint."""
	def decorator_wrapper(func):
		@api.doc(security="user")
		@api.response(401, "Authorization required")
		@api.response(403, "Authorization failed")
		@wraps(func)
		def wrapper(*args, **kwargs):
			verify_jwt_in_request()
			return func(*args, **kwargs)

		return wrapper
	return decorator_wrapper()


def admin_required(api):
	def decorator_wrapper(func):
		@api.doc(security="admin")
		@api.response(401, "Authorization required")
		@api.response(403, "Authorization failed or user not an administrator")
		@wraps(func)
		def wrapper(*args, **kwargs):
			verify_jwt_in_request()
			claims = get_jwt_claims()
			if "admin" not in claims or not claims["admin"]:
				abort(403, "User not an administrator")

			return func(*args, **kwargs)
		return wrapper
	return decorator_wrapper
