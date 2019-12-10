from flask_restplus import Resource


class RecordData(Resource):
	@staticmethod
	def post():
		"""Record a new bee observation"""
		return "Placeholder"

class Register(Resource):
	@staticmethod
	def get():
		"""Register"""
		return "Placeholder"

class Login(Resource):
	@staticmethod
	def get():
		"""Login"""
		return "Placeholder"

class Deregister(Resource):
	@staticmethod
	def get():
		"""Deregister (delete login)"""
		return "Placeholder"
