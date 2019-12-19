from logging import getLogger

log = getLogger()


def authenticate(func):
	"""Decorator for user authentication"""
	# TODO Implement authentication
	def wrapper(*args, **kwargs):
		log.info("Authenticating user \"{}\"".format("TODO"))
		return func(*args, **kwargs, user="username placeholder")
	return wrapper
