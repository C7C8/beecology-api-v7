from flask_restplus import Resource


class RelativePercent(Resource):
	@staticmethod
	def post():
		return "Hello from relative percent!"
