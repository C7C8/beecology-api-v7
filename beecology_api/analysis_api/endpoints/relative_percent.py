from flask_restx import Resource


class RelativePercent(Resource):
	@staticmethod
	def post():
		return "Hello from relative percent!"
