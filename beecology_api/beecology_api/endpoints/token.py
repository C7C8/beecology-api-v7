import base64
import datetime
from logging import getLogger

from firebase_admin import auth as firebase_auth
from flask import request
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_refresh_token_required, get_jwt_identity, \
	get_jwt_claims
from flask_restx import Resource, abort

from beecology_api import config
from beecology_api.beecology_api.api import main_api as api
from beecology_api.db import db_session
from beecology_api.db.models import User as DBUser
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
			abort(401, "Firebase basic token required")
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
				              registration_date=datetime.datetime.now(),
				              locked=False,
				              admin=False)
				session.add(user)

			user.last_login = datetime.datetime.now()
			session.commit()
			log.info("User {} logging in".format(user_id))
			return {
				       "access_token": create_access_token(identity=user.id,
				                                           user_claims={"admin": user.admin},
				                                           expires_delta=expires,
				                                           fresh=True),
				       "refresh_token": create_refresh_token(identity=user.id, user_claims={"admin": user.admin}),
				       "expires": datetime.datetime.now() + expires
			}


class Refresh(Resource):
	@api.doc(security="user-refresh")
	@api.marshal_with(jwt_response)
	@api.response(401, "Refresh token required")
	@api.response(403, "Refresh token authentication failed")
	@api.response(200, "New access token enclosed", jwt_response)
	@jwt_refresh_token_required
	def get(self):
		"""Get a JWT using a refresh token"""
		user = get_jwt_identity()
		log.info("User {} refreshing token".format(user))
		claims = get_jwt_claims()
		expires = datetime.timedelta(seconds=config.config["auth"]["token-lifetime"])
		return {
			"access_token": create_access_token(user, expires_delta=expires, user_claims=claims)
		}, 200
