from flask_restplus import Resource


class Flowerdex(Resource):
	@staticmethod
	def get():
		"""Get flower by ID"""
		return "Placeholder"

	@staticmethod
	def post():
		"""Create a new flower"""
		return "Placeholder"

	@staticmethod
	def put():
		"""Update a flower by ID"""
		return "Placeholder"

	@staticmethod
	def delete():
		"""Delete flower by ID"""
		return "Placeholder"

class FlowerShapes(Resource):
	@staticmethod
	def get():
		"""Get all flower shapes"""
		return "Placeholder"

class FlowerColors(Resource):
	@staticmethod
	def get():
		"""Get all flower colors"""
		return "Placeholder"

class UnmatchedFlowers(Resource):
	@staticmethod
	def get():
		"""Get unmatched flowers"""
		return "Placeholder"
