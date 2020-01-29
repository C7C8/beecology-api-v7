from flask import url_for
from flask_restx import Resource
from werkzeug.utils import redirect


class Index(Resource):
	def get(self):
		"""Return a \"Hello, world!\" message"""
		return "Hello, world!"


class Error(Resource):
	def get(self):
		"""Return generic error-style hello world message"""
		return "Oh no! You encoutered an error!"

class TestError(Resource):
	def get(self):
		"""Redirect to error page"""
		return redirect(url_for("api./analysis_error"))
