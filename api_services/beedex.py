from flask_restplus import Resource

class Beedex(Resource):
	@staticmethod
	def get():
		"""Get an entry from the beedex by ID"""
		return "Placeholder"
