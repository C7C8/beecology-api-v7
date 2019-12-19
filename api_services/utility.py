from logging import getLogger

log = getLogger()

def response(status: str, message: str, error: bool, data=None):
	ret = {
		"status": status,
		"message": message,
		"error": error
	}
	if data is not None:
		ret["data"] = data
	return ret


def cache_response(func):
	"""Decorator for caching responses"""
	# TODO Implement caching
	def wrapper(*args, **kwargs):
		if "invalidate_cache" in kwargs and kwargs["invalidate_cache"]:
			log.info("Invalidating cache for {} and returning new result".format(func.__name__))
		return func(*args, **kwargs)
	return wrapper

