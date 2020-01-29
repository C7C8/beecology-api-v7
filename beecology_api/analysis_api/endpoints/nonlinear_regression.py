from flask_restx import Resource


class NonlinearRegression(Resource):
	@staticmethod
	def post():
		return "Hello from nonlinear regression!"
