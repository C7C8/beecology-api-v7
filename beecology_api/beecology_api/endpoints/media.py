from flask_restx import Resource


class AddImage(Resource):
	def post(self):
		"""Upload a new image."""
		pass


class Image(Resource):
	def get(self):
		"""Get an image's file path."""
		pass

	def put(self):
		"""Change an existing image."""
		pass

	def delete(self):
		"""Delete an image."""
		pass


class AddVideo(Resource):
	def post(self):
		"""Upload a new video."""
		pass


class Video (Resource):
	def get(self):
		"""Get a video's file path."""
		pass

	def put(self):
		"""Change an existing video."""
		pass

	def delete(self):
		"""Delete a video."""
		pass
