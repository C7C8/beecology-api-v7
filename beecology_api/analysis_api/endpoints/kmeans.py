from flask_restx import Resource


class KMeans(Resource):
	@staticmethod
	def post():
		return "Hello from K Means!"
