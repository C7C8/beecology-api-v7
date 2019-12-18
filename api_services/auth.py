from logging import getLogger

log = getLogger()


def authenticate(func):
	"""Wrapper for user authentication"""
	# TODO Implement authentication
	def wrapper(*o_args, **o_kwargs):
		log.info("Authenticating user \"{}\"".format("TODO"))
		return func(*o_args, **o_kwargs, user="username placeholder")
	return wrapper
