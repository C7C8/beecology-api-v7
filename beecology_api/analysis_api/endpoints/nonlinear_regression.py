from flask_restplus import Resource


class NonlinearRegression(Resource):
	@staticmethod
	def post():
		return "Hello from nonlinear regression!"
