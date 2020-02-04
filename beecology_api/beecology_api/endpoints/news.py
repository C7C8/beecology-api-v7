from flask_restx import Resource

class AddNews(Resource):
	def post(self):
		"""Add a new news item."""
		pass


class News(Resource):
	def get(self):
		"""Get all news."""
		pass

	def put(self):
		"""Update a news item."""
		pass

	def delete(self):
		"""Delete a news item."""
		pass
