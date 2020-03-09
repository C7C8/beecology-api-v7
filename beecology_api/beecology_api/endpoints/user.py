from logging import getLogger

from flask import abort
from flask_restx import Resource
from marshmallow import ValidationError

from beecology_api.beecology_api.api import manage_api as api
from beecology_api.beecology_api.authentication import admin_required
from beecology_api.db import db_session, User as DBUser
from beecology_api.serialization import user_schema
from beecology_api.swagger import user

log = getLogger()

class User(Resource):
	@admin_required(api)
	@api.response(404, "Could not find user")
	@api.response(200, "User data enclosed")
	def get(self, id: str):
		"""Get information on one user."""
		with db_session() as session:
			user = session.query(DBUser).filter(DBUser.id == id).first()
			if user is None:
				abort(404)
			return user_schema.dump(user), 200

	@admin_required(api)
	@api.expect(user)
	@api.response(404, "Could not find user")
	@api.response(400, "Unknown field or data type")
	@api.response(204, "User updated")
	def put(self, id: str):
		with db_session() as session:
			if session.query(DBUser).filter(DBUser.id == id).first() is None:
				abort(404)

			try:
				user_schema.load(api.payload, session=session)
			except (ValueError, ValidationError) as e:
				log.error("Flask failed to validate input to Marshmallow's standards: {}".format(api.payload), e)
				abort(400, "Unknown field or data type")

			session.commit()
			return "", 204

	@admin_required(api)
	@api.response(204, "User deleted if present")
	def delete(self, id: str):
		"""Delete a user's record."""
		with db_session() as session:
			session.query(DBUser).filter(DBUser.id == id).delete()
			session.commit()
		return "", 204


class Users(Resource):
	@admin_required(api)
	@api.marshal_with(user, as_list=True)
	def get(self):
		"""Get information on all users."""
		with db_session() as session:
			return [user_schema.dump(user) for user in session.query(DBUser).all()], 200


# class ChangeAdmin(Resource):
# 	Determine whether put/post are correct here for admin verification and updating
	# def put(self):
	# 	"""Submit a verification code confirming the calling user is now an admin."""
	# 	pass
