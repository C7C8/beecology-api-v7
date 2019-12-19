import base64
import hashlib
from logging import getLogger
import magic
import uuid

from flask_restplus import Resource, reqparse

from .config import Config
from api_services.auth import authenticate
from api_services.utility import response

log = getLogger()


class UploadVideo(Resource):
	@staticmethod
	def post():
		"""Upload a video"""
		return "Placeholder"


class UploadImage(Resource):
	@staticmethod
	@authenticate
	def post(user=None):
		"""Upload an image in base64 and save it"""
		parser = reqparse.RequestParser()
		parser.add_argument("recordImage", type=str, required=True)
		args = parser.parse_args()

		# Decode file from base64, then make sure it's actually an image
		mime = magic.Magic(mime=True)
		data = base64.standard_b64decode(args["recordImage"])
		mime_type = mime.from_buffer(data)
		if mime_type.find("image/") == -1:
			log.warning("User {} attempted to upload file with wrong MIME type, {}".format(user, mime_type))
			return response("false", "Received file but was of type {} instead of image/*".format(mime_type), True)

		# Save image file to UUID-based name, with an extension determined by the file's MIME type
		# Using a UUID allows us to guarantee unique filenames while embedding user and time information
		# The node computation takes the SHA-1 of the username (similar to the original Node server) and
		# uses it as the node value mod 2^48 (node values are 48 bits). This lets us embed user info in
		# the filename, but not in a back-traceable way.
		node = None if user is None else int(hashlib.sha1(user.encode("utf-8")).hexdigest(), 16) % (1 << 48)
		filename = "{dir}/{uuid}.{ext}".format(dir=Config.config["storage"]["imageUploadPath"],
		                                       uuid=uuid.uuid1(node=node),
		                                       ext=mime_type.split("/")[1])
		log.info("Saving image to {}".format(filename))
		with open(filename, "wb") as file:
			file.write(data)

		res = response("success", "upload image success", False)
		res["imagePath"] = filename
		return res, 200
