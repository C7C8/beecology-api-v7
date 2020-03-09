from logging import getLogger
from uuid import uuid4, UUID

from flask_restx import Resource, abort
from marshmallow import ValidationError

from beecology_api.beecology_api.api import main_api as api
from beecology_api.beecology_api.authentication import admin_required
from beecology_api.db import db_session, News as DBNews
from beecology_api.serialization import news_schema
from beecology_api.swagger import news_item, news_filter_parser

log = getLogger()

class News(Resource):
	@api.expect(news_item)
	@api.response(400, "Invalid input")
	@api.response(201, "Added news item")
	@admin_required(api)
	def post(self):
		"""Add a new news item."""
		api.payload["id"] = uuid4()
		with db_session() as session:
			try:
				news = news_schema.load(api.payload, session=session)
			except (ValueError, ValidationError) as e:
				log.error("Flask failed to validate input to Marshmallow's standards: {}".format(api.payload), e)
				abort(400, "Invalid input")

			session.add(news)
			session.commit()

		log.info("Added new news item {}".format(news.id))
		return {"message": "News item {} added".format(id)}, 201

	@api.expect(news_filter_parser)
	@api.marshal_with(news_item, as_list=True)
	@api.response(400, "Bad filter parameters")
	def get(self):
		"""Get all news, subject to optional filtering"""
		args = news_filter_parser.parse_args()
		with db_session() as session:
			query = session.query(DBNews)

			if "type" in args:
				query = query.filter(DBNews.type == args["type"])
			if "before" in args:
				query = query.filter(DBNews.posted <= args["before"])
			if "after" in args:
				query = query.filter(DBNews.posted >= args["after"])

			return [news_schema.dump(news) for news in query.all()], 200

	@api.param("id", "UUID of news item to update")
	@api.expect(news_item)
	@api.response(204, "News item updated")
	@api.response(404, "News item not found")
	@api.response(400, "Unknown field or data type")
	@admin_required(api)
	def put(self, id: UUID):
		"""Update a news item. Changes to ID or user ID are ignored"""
		api.payload["id"] = id
		if "user_id" in api.payload:
			del api.payload["user_id"]

		with db_session() as session:
			if session.query(DBNews).filter(DBNews.id == id).first() is None:
				abort(404)

			try:
				news_schema.load(api.payload, session=session)
			except (ValueError, ValidationError):
				log.error("Flask failed to validate input to Marshmallow's standards: {}".format(api.payload), e)
				abort(400, "Unknown field or data type")

		session.commit()
		return "", 204

	@api.param("id", "UUID of news item to delete")
	@api.response(204, "News item deleted (if present)")
	@admin_required(api)
	def delete(self, id: UUID):
		"""Delete a news item."""
		with db_session() as session:
			session.query(DBNews).filter(DBNews.id == id).delete()
			session.commit()
		return "", 204
