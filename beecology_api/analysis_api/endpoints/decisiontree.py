from flask_restplus import Resource


class DecisionTree(Resource):
	@staticmethod
	def post():
		return "Hello from decision tree!"
