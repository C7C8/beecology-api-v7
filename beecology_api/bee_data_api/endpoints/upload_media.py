import base64
import hashlib
import uuid
from logging import getLogger

import magic
from flask_restplus import Resource

from beecology_api import config
from beecology_api.bee_data_api.api import api
from beecology_api.bee_data_api.authentication import authenticate
from beecology_api.bee_data_api.models import video_parser, image_parser, media_upload_response, response_wrapper
from beecology_api.bee_data_api.response import response

log = getLogger()


class UploadVideo(Resource):
	@api.expect(video_parser)
	@api.response(200, "Video uploaded, path enclosed", media_upload_response)
	@api.response(400, "Media received but had incorrect MIME type", response_wrapper)
	@authenticate
	def post(self, user):
		"""Upload a video in base64 and save it. Returns file path."""
		args = video_parser.parse_args()
		return process_media(args["recordVideo"], "video", user)


class UploadImage(Resource):
	@api.expect(image_parser)
	@api.response(200, "Image uploaded, path enclosed", media_upload_response)
	@api.response(400, "Media received but had incorrect MIME type", response_wrapper)
	@authenticate
	def post(self, user=None):
		"""Upload an image in base64 and save it. Returns file path."""
		args = image_parser.parse_args()
		return process_media(args["recordImage"], "image", user)


def process_media(b64, mime_type, user):
	"""Process a media file from base64, validating its mime type in the process."""
	data = base64.urlsafe_b64decode(b64 + ("=" * (4 - len(b64) % 4)))
	mime = magic.Magic(mime=True)
	file_type = mime.from_buffer(data)
	if file_type.find(mime_type) == -1:
		log.warning("User {} attempted to upload file with wrong MIME type, {}".format(user, file_type))
		return response("false", "Received file but was of type {} instead of {}/*".format(file_type, mime_type), True), 400

	# Save image file to UUID-based name, with an extension determined by the file's MIME type
	# Using a UUID allows us to guarantee unique filenames while embedding user and time information
	# The node computation takes the SHA-1 of the username (similar to the original Node server) and
	# uses it as the node value mod 2^48 (node values are 48 bits). This lets us embed user info in
	# the filename, but not in a back-traceable way.
	node = None if user is None else int(hashlib.sha1(user.encode("utf-8")).hexdigest(), 16) % (1 << 48)
	file = "{uuid}.{ext}".format(uuid=uuid.uuid1(node=node), ext=file_type.split("/")[1])
	filename = config.config["storage"]["imageUploadPath"] + "/" + file
	log.info("Saving image to {}".format(filename))
	with open(filename, "wb") as file:
		file.write(data)

	res = response("success", "upload image success", False)
	res["imagePath"] = config.config["storage"]["imageBasePath"] + "/" + file
	return res, 200
