from flask_restx import Resource


class DecisionTree(Resource):
	@staticmethod
	def post():
		return "Hello from decision tree!"
