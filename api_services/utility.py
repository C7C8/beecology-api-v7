from api_services.cache import invalidate_caches


def response(status: str, message: str, error: bool, data=None):
	ret = {
		"status": status,
		"message": message,
		"error": error
	}
	if data is not None:
		ret["data"] = data
	return ret



