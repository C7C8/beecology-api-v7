from flask_restplus import Resource


class LinearRegression(Resource):
	@staticmethod
	def post():
		return "Hello from linear regression!"
