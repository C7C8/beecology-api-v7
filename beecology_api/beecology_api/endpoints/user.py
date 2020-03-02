import base64
import datetime
from logging import getLogger

from firebase_admin import auth as firebase_auth
from flask import request, abort
from flask_jwt_extended import create_access_token, create_refresh_token
from flask_restx import Resource

from beecology_api import config
from beecology_api.beecology_api.api import main_api as api
from beecology_api.db import db_session, User as DBUser
from beecology_api.swagger import jwt_response

log = getLogger()


class Token(Resource):
	@api.doc(security="firebase")
	@api.marshal_with(jwt_response)
	@api.response(401, "Firebase basic token required")
	@api.response(403, "Firebase token authentication failed")
	@api.response(200, "Access and refresh tokens enclosed", jwt_response)
	def get(self):
		"""Get a JWT for authentication using Firebase credentials."""
		if "Authorization" not in request.headers:
			abort(401, "Firebae basic token required")
		try:
			token = base64.standard_b64decode(request.headers["Authorization"].split(" ")[1])
			user_data = firebase_auth.verify_id_token(token)
		except Exception as e:
			log.info("User failed authentication: {}".format(e))
			abort(403, "Failed to authenticate: {}".format(e))

		# Try to load the user from the database. If they exist, return a token immediately with admin dependent on DB
		# results. If they don't, create a new entry for them with admin disabled.
		user_id = user_data["uid"]
		expires = datetime.timedelta(seconds=config.config["auth"]["token-lifetime"])
		with db_session() as session:
			user: DBUser = session.query(DBUser).filter(DBUser.id == user_id).first()
			if user is None:
				user = DBUser(id=user_id,
				              email=user_data["email"],
				              registration_date=datetime.datetime.now(),
				              locked=False,
				              admin=False)
				session.add(user)

			user.last_login = datetime.datetime.now()
			session.commit()
			return {
				       "access_token": create_access_token(identity=user.id,
				                                           user_claims={"admin": user.admin},
				                                           expires_delta=expires,
				                                           fresh=True),
				       "refresh_token": create_refresh_token(identity=user.id, user_claims={"admin": user.admin}),
				       "expires": datetime.datetime.now() + expires
			}


class Refresh(Resource):
	@api.doc(security="user")
	def get(self):
		"""Get a JWT using a refresh token"""
		pass


class User(Resource):
	def get(self):
		"""Get information on one or all users."""
		pass

	def put(self):
		"""Make changes to a user's record."""
		pass

	def delete(self):
		"""Delete a user's record."""


class ChangeAdmin(Resource):
	# TODO Determine whether put/post are correct here for admin verification and updating
	def put(self):
		"""Submit a verification code confirming the calling user is now an admin."""
		pass


class Admin(Resource):
	def get(self):
		"""Get information on one or more admins."""

	def post(self):
		"""Update another user's admin privileges."""
		pass

	def delete(self):
		"""Remove self as user. For safety reasons this can't be done by POST to this resource."""
