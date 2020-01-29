from flask_restplus import Resource


class Trend(Resource):
	@staticmethod
	def post():
		return "Hello from trend!"
