import base64
import binascii
import hashlib
import os
from datetime import datetime
from logging import getLogger
from uuid import uuid1, UUID

import magic
from flask_jwt_extended import get_jwt_identity
from flask_restx import Resource, abort

from beecology_api import config
from beecology_api.beecology_api.api import main_api as api
from beecology_api.beecology_api.authentication import authenticate
from beecology_api.db import db_session
from beecology_api.db import Media as DBMedia, User
from beecology_api.serialization import media_schema
from beecology_api.swagger import media_upload_parser, media

log = getLogger()


class Media(Resource):
	@api.expect(media_upload_parser)
	@api.response(415, "Incorrect file upload MIME type or decoding failure")
	@api.response(413, "Upload exceeded file size limit")
	@api.response(201, "Image uploaded", media)
	@authenticate(api)
	def post(self):
		"""Upload a new media item"""
		args = media_upload_parser.parse_args()
		id, file_path, web_path, mime_type = _process_media(b64=args["data"], user=get_jwt_identity())
		db_media = DBMedia(id=id, file_path=file_path, web_path=web_path, user_id=get_jwt_identity(), type=mime_type)
		with db_session() as session:
			session.add(db_media)
			session.commit()
			return media_schema.dump(db_media), 201

	@api.param("id", "Image UUID")
	@api.response(404, "Image not found")
	@api.response(200, "Image found", media)
	def get(self, id: UUID):
		"""Get information for a media item by ID"""
		with db_session() as session:
			db_media = session.query(DBMedia).filter(DBMedia.id == id).first()
			if db_media is None:
				abort(404)
			return media_schema.dump(db_media), 200

	@api.param("id", "Image UUID")
	@api.expect(media_upload_parser)
	@api.response(415, "Incorrect file upload MIME type or decoding failure")
	@api.response(413, "Upload exceeded file size limit")
	@api.response(404, "Media not found")
	@api.response(403, "Media update disallowed")
	@api.response(204, "Media updated")
	@authenticate(api)
	def put(self, id: UUID):
		"""Change an existing media item."""
		args = media_upload_parser.parse_args()
		with db_session() as session:
			# First get the original media record so we can reuse its ID and delete the original file
			media: DBMedia = session.query(DBMedia).filter(DBMedia.id == id).first()
			if media is None:
				abort(404)

			# Check to make sure the current user owns the file or is an admin
			if media.user_id != get_jwt_identity() and not session.query(User).filter(User.id == get_jwt_identity()).first().admin:
				abort(403)

			# Process the new media file
			id, file_path, client_path, mime_type = _process_media(b64=args["data"], user=get_jwt_identity())

			# Since no HTTPException was thrown, it worked and the file is now stored on-disk. Delete the old file,
			# and update the database records to match the new file.
			os.remove(media.file_path)
			media.client_path = client_path
			media.file_path = file_path
			media.uploaded = datetime.now()
			media.type = mime_type
			session.commit()

		return "", 204

	@api.param("id", "Media UUID")
	@api.response(204, "Media deleted")
	@api.response(404, "Media not found")
	@api.response(403, "Media delete disallowed")
	@authenticate(api)
	def delete(self, id: UUID):
		"""Delete a media item"""
		with db_session() as session:
			db_media = session.query(DBMedia).filter(DBMedia.id == id).first()
			if db_media is None:
				abort(404)
			if db_media.user_id != get_jwt_identity() and not session.query(User).filter(User.id == get_jwt_identity()).first().admin:
				abort(403)

			os.remove(db_media.file_path)
			session.delete(db_media)
			session.commit()
		return "", 204


def _process_media(b64: str, user: str) -> (UUID, str, str):
	"""Process a media file from base 64. Returns the UUID, file path, client-visible path, and mime type"""
	try:
		data = base64.b64decode(b64)
	except binascii.Error as e:
		log.warning("Got a bad upload", e)
		abort(415, "Failed to decode base 64, check your encoding")

	mime = magic.Magic(mime=True)
	upload_mime_type = mime.from_buffer(data)
	if "video" not in upload_mime_type and "image" not in upload_mime_type:
		log.warning("User {} attempted to upload file with wrong MIME type, {}".format(user, upload_mime_type))
		abort(415, "Received file but was of type {} instead of video/* or image/*".format(upload_mime_type))

	max_size = config.config["storage"]["imageMaxSize"] if "image" in upload_mime_type else config.config["storage"]["videoMaxSize"]
	if len(data) > max_size:
		abort(413, "Upload size exceeded {} bytes".format(max_size))

	node = None if user is None else int(hashlib.sha1(user.encode("utf-8")).hexdigest(), 16) % (1 << 48)
	id = uuid1(node=node)
	file_name = "{uuid}.{ext}".format(uuid=id, ext=upload_mime_type.split("/")[1])
	file_path = "{path}/{file_name}".format(path=config.config["storage"]["mediaUploadPath"], file_name=file_name)
	with open(file_path, "wb") as file:
		file.write(data)

	client_path = config.config["storage"]["mediaBasePath"] + "/" + file_name
	return id, file_path, client_path, upload_mime_type
