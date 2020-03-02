import base64
import binascii
import hashlib
import os
from datetime import datetime
from logging import getLogger
from uuid import uuid1, UUID

import magic
from flask_restx import Resource, abort

from beecology_api import config
from beecology_api.beecology_api.api import main_api as api
from beecology_api.db import db_session
from beecology_api.db import Image as DBImage, Video as DBVideo
from beecology_api.serialization import image_schema, video_schema
from beecology_api.swagger import media_upload_parser, media

log = getLogger()


class Image(Resource):
	@api.expect(media_upload_parser)
	@api.response(415, "Incorrect file upload MIME type or decoding failure")
	@api.response(413, "Upload exceeded file size limit")
	@api.response(201, "Image uploaded", media)
	def post(self):
		"""Upload a new image"""
		# TODO require auth
		# Process media of image/* mime type and a max file size of 10 MB
		args = media_upload_parser.parse_args()
		id, file_path, client_path = _process_media(b64=args["data"], mime_type="image", max_size=10**7)
		image = DBImage(id=id, file_path=file_path, client_path=client_path)
		with db_session() as session:
			session.add(image)
			session.commit()
			return image_schema.dump(image), 201

	@api.param("id", "Image UUID")
	@api.response(404, "Image not found")
	@api.response(200, "Image found", media)
	def get(self, id: UUID):
		"""Get image data"""
		with db_session() as session:
			image = session.query(DBImage).filter(DBImage.id == id).first()
			if image is None:
				abort(404)
			return image_schema.dump(image), 200

	@api.param("id", "Image UUID")
	@api.expect(media_upload_parser)
	@api.response(415, "Incorrect file upload MIME type or decoding failure")
	@api.response(413, "Upload exceeded file size limit")
	@api.response(404, "Image not found")
	@api.response(204, "Image updated")
	def put(self, id: UUID):
		"""Change an existing image."""
		# TODO require auth
		args = media_upload_parser.parse_args()
		with db_session() as session:
			# First get the original image record so we can reuse its ID and delete the original file
			image = session.query(DBImage).filter(DBImage.id == id).first()
			if image is None:
				abort(404)

			# Process the new media file
			id, file_path, client_path = _process_media(b64=args["data"], mime_type="image", max_size=10**7)

			# Since no HTTPException was thrown, it worked and the file is now stored on-disk. Delete the old file,
			# and update the database records to match the new file.
			os.remove(image.file_path)
			image.client_path = client_path
			image.file_path = file_path
			image.uploaded = datetime.now()
			session.commit()

		return "", 204

	@api.param("id", "Image UUID")
	@api.response(204, "Image deleted")
	@api.response(404, "Image not found")
	def delete(self, id: UUID):
		"""Delete an image."""
		# TODO require auth
		with db_session() as session:
			image = session.query(DBImage).filter(DBImage.id == id).first()
			if image is None:
				abort(404)

			os.remove(image.file_path)
			session.delete(image)
			session.commit()
		return "", 204


class Video(Resource):
	@api.expect(media_upload_parser)
	@api.response(415, "Incorrect file upload MIME type or decoding failure")
	@api.response(413, "Upload exceeded file size limit")
	@api.response(201, "Video uploaded")
	def post(self):
		"""Upload a new video."""
		# TODO require auth
		# Process media of video/* mime type and a max file size of 100 MB
		args = media_upload_parser.parse_args()
		id, file_path, client_path = _process_media(b64=args["data"], mime_type="video", max_size=10**8)
		video = DBVideo(id=id, file_path=file_path, client_path=client_path)
		with db_session() as session:
			session.add(video)
			session.commit()
		return video_schema.dump(video), 201

	@api.param("id", "Video UUID")
	@api.response(404, "Video not found")
	@api.response(200, "Video found", media)
	def get(self, id: UUID):
		"""Get a video's file path."""
		with db_session() as session:
			video = session.query(DBVideo).filter(DBVideo.id == id).first()
			if video is None:
				abort(404)
			return video_schema.dump(video), 200

	@api.param("id", "Video UUID")
	@api.expect(media_upload_parser)
	@api.response(415, "Incorrect file upload MIME type or decoding failure")
	@api.response(413, "Upload exceeded file size limit")
	@api.response(404, "Video not found")
	@api.response(204, "Video updated")
	def put(self, id: UUID):
		"""Change an existing video."""
		# TODO require auth
		args = media_upload_parser.parse_args()
		with db_session() as session:
			# First get the original video record so we can reuse its ID and delete the original file
			video = session.query(DBVideo).filter(DBVideo.id == id).first()
			if video is None:
				abort(404)

			# Process the new media file
			id, file_path, client_path = _process_media(b64=args["data"], mime_type="video", max_size=10**8)

			# Since no HTTPException was thrown, it worked and the file is now stored on-disk. Delete the old file,
			# and update the database records to match the new file.
			os.remove(video.file_path)
			video.client_path = client_path
			video.file_path = file_path
			video.uploaded = datetime.now()
			session.commit()

		return "", 204

	@api.param("id", "Video UUID")
	@api.response(204, "Video deleted")
	@api.response(404, "Video not found")
	def delete(self, id: UUID):
		"""Delete a video."""
		# TODO require auth
		with db_session() as session:
			video = session.query(DBVideo).filter(DBVideo.id == id).first()
			if video is None:
				abort(404)

			os.remove(video.file_path)
			session.delete(video)
			session.commit()
		return "", 204


def _process_media(b64: str, mime_type: str, user: str = None, max_size: int = None) -> (UUID, str, str):
	"""Process a media file from base 64. Returns the UUID, file path, and client-visible path of the file"""
	# TODO Remove user=None by default when auth is implemented properly
	try:
		data = base64.b64decode(b64)
	except binascii.Error as e:
		log.warning("Got a bad upload", e)
		abort(415, "Failed to decode base 64, check your encoding")

	if max_size is not None and len(data) > max_size:
		abort(413, "Upload size exceeded {} bytes".format(max_size))

	mime = magic.Magic(mime=True)
	upload_mime_type = mime.from_buffer(data)
	if mime_type not in upload_mime_type:
		log.warning("User {} attempted to upload file with wrong MIME type, {}".format(user, upload_mime_type))
		abort(415, "Received file but was of type {} instead of {}/*".format(upload_mime_type, mime_type))

	node = None if user is None else int(hashlib.sha1(user.encode("utf-8")).hexdigest(), 16) % (1 << 48)
	id = uuid1(node=node)
	file_name = "{uuid}.{ext}".format(uuid=id, ext=upload_mime_type.split("/")[1])
	file_path = "{path}/{file_name}".format(path=config.config["storage"]["imageUploadPath"], file_name=file_name)
	with open(file_path, "wb") as file:
		file.write(data)

	client_path = config.config["storage"]["imageBasePath"] + "/" + file_name
	return id, file_path, client_path
