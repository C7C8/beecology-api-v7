from flask_restplus import Resource


class IsConnected(Resource):
	def get(self):
		"""Return a simple 'yes, the app is working'-style message. Useful to tell whether the web app can talk to the
		server or not."""
		return {"message": "Welcome! The api is working!"}
