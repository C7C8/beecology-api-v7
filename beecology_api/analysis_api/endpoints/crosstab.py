from flask_restx import Resource


class CrossTabulation(Resource):
	@staticmethod
	def post():
		return "Hello from cross tabulation!"
