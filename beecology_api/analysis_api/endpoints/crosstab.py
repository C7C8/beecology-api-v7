from flask_restplus import Resource


class CrossTabulation(Resource):
	@staticmethod
	def post():
		return "Hello from cross tabulation!"
