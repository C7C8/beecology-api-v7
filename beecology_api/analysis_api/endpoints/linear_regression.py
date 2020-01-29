from flask_restx import Resource


class LinearRegression(Resource):
	@staticmethod
	def post():
		return "Hello from linear regression!"
