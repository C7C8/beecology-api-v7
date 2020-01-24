from flask_restplus import Resource, reqparse
from sqlalchemy import sql

from beecology_api import config
from beecology_api.api import database
from beecology_api.api.authentication import authenticate


class VerifyAdmin(Resource):
	@staticmethod
	@authenticate
	def post(user):
		"""Activate self (logged in user) as an administrator by using a confidential activation code."""
		parser = reqparse.RequestParser()
		parser.add_argument("activationCode", type=str, required=False)
		args = parser.parse_args()

		engine = database.get_engine()
		results = engine.execute(sql.select([database.admin]).where(database.admin.c.user_id == user))
		if len(next(results, {})) > 0:
			# User is already an admin
			return {"sucess": True}, 200  # TODO: Fix typo

		# User is not an admin, check the activation code; if it matches, add them to the admins list
		if "activationCode" in args and args["activationCode"] == config.config["admin-code"]:
			engine.execute(sql.insert(database.admin).values(user_id=user))
			return {"sucess": True}, 200  # TODO: Fix typo

		return "Not authorized", 403
