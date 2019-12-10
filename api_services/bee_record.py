from flask_restplus import Resource


class BeeRecord(Resource):
	@staticmethod
	def get():
		"""Get a bee record by ID"""
		return "Placeholder"

	@staticmethod
	def put():
		"""Update a bee record by ID"""
		return "Placeholder"

	@staticmethod
	def delete():
		"""Delete a bee record by ID"""
		return "Placeholder"

class BeeRecordsList(Resource):
	@staticmethod
	def get():
		"""Get bee records by page"""
		return "Placeholder"

class BeeVisRecords(Resource):
	@staticmethod
	def get():
		"""Get all bee records"""
		return "Placeholder"

class BeeUserRecords(Resource):
	@staticmethod
	def get():
		"""Get bee log records by user ID"""
		return "Placeholder"
