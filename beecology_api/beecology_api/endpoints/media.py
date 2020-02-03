from flask_restx import Resource

class Image(Resource):
	def get(self):
		"""Get an image's file path."""
		pass

	def post(self):
		"""Upload a new image."""
		pass

	def put(self):
		"""Change an existing image."""
		pass

	def delete(self):
		"""Delete an image."""
		pass


class Video (Resource):
	def get(self):
		"""Get a video's file path."""
		pass

	def post(self):
		"""Upload a new video."""
		pass

	def put(self):
		"""Change an existing video."""
		pass

	def delete(self):
		"""Delete a video."""
		pass
