from flask_restx import Resource


class AddBee(Resource):
	def post(self):
		"""Add a new bee species"""
		pass


class Bee(Resource):
	def get(self):
		"""Get information on one or all bee species."""
		pass

	def put(self):
		"""Update a bee species."""
		pass

	def delete(self):
		"""Delete a bee species."""
		pass
