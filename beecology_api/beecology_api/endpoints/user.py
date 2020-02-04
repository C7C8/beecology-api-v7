from flask_restx import Resource


class Token(Resource):
	def get(self):
		"""Get a JWT for authentication using Firebase credentials."""
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
