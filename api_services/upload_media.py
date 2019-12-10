from flask_restplus import Resource


class UploadVideo(Resource):
	@staticmethod
	def post():
		"""Upload a video"""
		return "Placeholder"

class UploadImage(Resource):
	@staticmethod
	def post():
		"""Upload an image"""
		return "Placeholder"
