from flask_restplus import Resource


class RecordData(Resource):
	@staticmethod
	def post():
		"""Record a new bee observation"""
		return "Placeholder"

class Enroll(Resource):
	@staticmethod
	def get():
		"""Register"""
		return "Placeholder"

class Refresh(Resource):
	@staticmethod
	def get():
		"""Login"""
		return "Placeholder"

class Unenroll(Resource):
	@staticmethod
	def get():
		"""Deregister (delete login)"""
		return "Placeholder"
