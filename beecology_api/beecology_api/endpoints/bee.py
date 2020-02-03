from flask_restx import Resource


class Bee(Resource):
	def get(self):
		"""Get information on one or all bee species."""
		pass

	def post(self):
		"""Add a new bee species, or replace an existing one."""
		pass

	def put(self):
		"""Update a bee species."""
		pass

	def delete(self):
		"""Delete a bee species."""
		pass
