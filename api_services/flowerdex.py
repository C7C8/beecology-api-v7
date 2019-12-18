from logging import getLogger

import sqlalchemy as sql
from flask_restplus import Resource, reqparse
from sqlalchemy import and_, func

from api_services.database import Database
from api_services.util import response

log = getLogger()

class Flowerdex(Resource):
	@staticmethod
	def get(id: int = -1):
		"""Get flower by ID"""
		log.info("Getting flowerdex ID {}".format(id if id != -1 else "*"))
		with Database() as engine:
			flower = Database.flowerdict
			query = sql.select([flower.c.flower_id,
			                    flower.c.latin_name.label("flower_latin_name"),
			                    flower.c.main_common_name.label("flower_common_name")])
			if id != -1:
				query = query.where(Database.flowerdict.c.flower_id == id)
			results = engine.execute(query)

			data = [dict(r) for r in results]
			if len(data) == 0:
				return response("false", "Flower not found!", True), 404

			log.info("Returning {} flowerdex entries".format(len(data)))
			return response("success", "Retrieve the Flower information success!", False, data=data), 200

	@staticmethod
	def post():
		"""Create a new flower"""
		parser = reqparse.RequestParser()
		parser.add_argument("flowercommonname", required=True, type=str, dest="flower_common_name")
		parser.add_argument("flowershapeid", required=True, type=str, dest="flower_shape")
		parser.add_argument("flowercolorid", required=True, type=str, dest="flower_color"),
		parser.add_argument("flowerspecies", required=True, type=str, dest="flower_species"),
		parser.add_argument("flowergenus", required=True, type=str, dest="flower_genus")
		args = parser.parse_args()
		log.info("Adding flower {}".format(args))

		with Database() as engine:
			query = sql.insert(Database.flower).values(**args).returning(Database.flower.c.flower_id)
			result = engine.execute(query)
			id = dict(next(result))
			if id is None:
				return response("false", "Log a new flower failed", True), 405
			return response("success", "Log a new flower success!", False, data=id), 200

	@staticmethod
	def put(id: int):
		"""Update a flower by ID"""
		parser = reqparse.RequestParser()
		parser.add_argument("fcommon", required=False, type=str, dest="flower_common_name")
		parser.add_argument("fshape", required=False, type=str, dest="flower_shape")
		parser.add_argument("fcolor", required=False, type=str, dest="flower_color")
		parser.add_argument("fspecies", required=False, type=str, dest="flower_species")
		parser.add_argument("fgenus", required=False, type=str, dest="flower_genus")
		args = parser.parse_args()
		args = {k: v for k, v in args.items() if v is not None}

		log.info("Updating flower {}".format(id))
		with Database() as engine:
			query = sql.update(Database.flower).values(**args).where(Database.flower.c.flower_id == id).returning(Database.flower.c.flower_id)
			result = engine.execute(query)
			id = dict(next(result, {}))
			if len(id) == 0:
				return response("false", "Flower not found!", True), 404
			return response("success", "Update the Folwer information success!", False, data=id), 200  # TODO Fix typo

	@staticmethod
	def delete(id: int):
		"""Delete flower by ID"""
		log.info("Deleting flower {}".format(id))
		with Database() as engine:
			query = sql.delete(Database.flower).where(Database.flower.c.flower_id == id).returning(Database.flower.c.flower_id)
			if next(engine.execute(query), None) is None:
				return response("false", "flower id not found!", True), 404
			return response("success", "Delete flower success!", False), 200


class FlowerShapes(Resource):
	@staticmethod
	def get():
		"""Get all flower shapes"""
		with Database() as engine:
			features = Database.features
			results = engine.execute(sql.select([features]).where(features.c.feature_id.like("fc%")))
			data = [dict(r) for r in results]
			if len(data) == 0:
				return response("false", "Flower shapes not found!", True)
			return response("success", "Retrieve the flower shapes success!", False, data=data)

class UnmatchedFlowers(Resource):
	@staticmethod
	def get():
		"""Get unmatched flowers"""
		with Database() as engine:
			bee = Database.beerecord
			flower = Database.flowerdict
			query = sql.select([
				bee.c.flower_name,
				func.count().label("count")
			]).select_from(
				bee.join(flower, bee.c.flower_name == flower.c.latin_name, isouter=True)
			).where(
				and_(flower.c.latin_name.is_(None), bee.c.flower_name.isnot(None))
			).group_by(bee.c.flower_name).order_by(bee.c.flower_name)

			results = engine.execute(query)
			data = [dict(r) for r in results]
			if len(data) == 0:
				return response("false", "Bee records not found!", True), 404  # TODO Change messages
			return response("success", "Retrieve the Bee records success!", False, data=data), 200
