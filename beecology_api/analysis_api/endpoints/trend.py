from flask_restx import Resource


class Trend(Resource):
	@staticmethod
	def post():
		return "Hello from trend!"
