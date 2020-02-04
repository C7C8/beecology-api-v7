from flask_restx import Resource


class AddFlower(Resource):
	def post(self):
		"""Add a new flower species, or replace an existing one."""
		pass


class Flower(Resource):
	def get(self):
		"""Get information on one or all flower species."""
		pass

	def put(self):
		"""Update a flower species."""
		pass

	def delete(self):
		"""Delete a flower species."""
		pass
