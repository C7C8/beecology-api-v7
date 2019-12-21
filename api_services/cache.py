import json
import os
import uuid
from logging import getLogger

from .config import Config

log = getLogger()


def invalidate_caches(*cache_args):
	"""Decorator for invalidating specified caches. Yes, the mess of functions below really is needed, this is how Python
	does decorators with arguments..."""
	def decorator_wrapper(func):
		def invalidates(*args, **kwargs):
			for cache in cache_args:
				log.debug("Invalidating cache name \"{}\"".format(cache))
				if cache not in invalidate_caches.caches:
					continue
				for wrapper in invalidate_caches.caches[cache]:
					wrapper.invalidate()
			return func(*args, **kwargs)
		return invalidates
	return decorator_wrapper


invalidate_caches.caches = {}

class cache_response:
	"""Decorator class for caching responses from a function. IMPORTANT: This must be the *first* decorator -- before
	any others, so the results from the actual function get cached."""
	def __init__(self, *args):
		self.cache = {}

		# If this cache has a defined cache name, add it to the global caches list.
		if args is not None:
			for cache_name in args:
				log.debug("Registering cache name \"{}\"".format(cache_name))
				if cache_name not in invalidate_caches.caches:
					invalidate_caches.caches[cache_name] = [self]
				else:
					invalidate_caches.caches[cache_name].append(self)

	def __call__(self, func, *args, **kwargs):
		"""Return cached response if present, otherwise call function and store in cache"""
		def cache(*args, **kwargs):
			key = frozenset([*args, *tuple(kwargs.items())])

			# Check cache to see if we have something by this key stored; if we do, load it from the on-disk cache and
			# return it. If we don't, call the original function and write its results out to the cache. Only the JSON
			# response from the function is stored on disk, the return code is stored in memory since it's so small.
			if key in self.cache:
				file_name, status_code = self.cache[key]
				log.debug("Returning cached response {}/{} for {}".format(file_name, status_code, func.__qualname__))
				with open(file_name, "r") as cached_file:
					# Parsing from JSON is necessary so Flask will send this back as a JSON object and not a string
					# TODO Remove JSON parsing step to improve cache performance if possible
					result = json.load(cached_file)
			else:
				cache_dir = Config.config["storage"]["cache"]
				result, status_code = func(*args, **kwargs)
				filename = "{cache_dir}/{qualname}-{uuid}.json".format(cache_dir=cache_dir,
				                                                       qualname=func.__qualname__.lower(),
				                                                       uuid=uuid.uuid4())
				log.info("Saving response from {qualname} to file {file}".format(qualname=func.__qualname__, file=filename))
				try:
					# Attempt to create the cache directory if it doesn't already exist, then dump the response out to file
					os.makedirs(cache_dir, exist_ok=True)
					with open(filename, "w") as file:
						json.dump(result, file)
					self.cache[key] = (filename, status_code)
				except (IOError or OSError) as e:
					log.error("Failed to write file {} to cache: {}".format(filename, e))

			return result, status_code
		return cache

	def invalidate(self):
		"""Invalidate everything stored in this cache"""
		for file_name, _ in self.cache.values():
			log.debug("Deleting cached file {}".format(file_name))
			try:
				os.remove(file_name)
			except IOError:
				log.error("Error deleting cached file {}".format(file_name))
		self.cache.clear()
