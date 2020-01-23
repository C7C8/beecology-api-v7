from flask_restplus import Resource


class Root(Resource):
	@staticmethod
	def get():
		"""Return a simple 'yes, the app is working'-style message"""
		return {"message": "Welcome! The api is working!"}
