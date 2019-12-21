from logging import getLogger

import sqlalchemy as sql
from flask_restplus import Resource, reqparse
from sqlalchemy import and_, func

from api_services import database
from .authentication import authenticate, admin_required
from .utility import response
from .cache import invalidate_caches, cache_response

log = getLogger()

class Flowerdex(Resource):
	@staticmethod
	@cache_response("flowerdict")
	def get(id: int = -1):
		"""Get flower by ID"""
		log.debug("Getting flowerdex ID {}".format(id if id != -1 else "*"))
		engine = database.get_engine()
		flower = database.flowerdict
		query = sql.select([flower.c.flower_id,
		                    flower.c.latin_name.label("flower_latin_name"),
		                    flower.c.main_common_name.label("flower_common_name")])
		if id != -1:
			query = query.where(database.flowerdict.c.flower_id == id)
		results = engine.execute(query)

		data = [dict(r) for r in results]
		if len(data) == 0:
			log.warning("Failed to retrieve flower #{}".format(id))
			return response("false", "Flower not found!", True), 404

		log.debug("Returning {} flowerdex entries".format(len(data)))
		return response("success", "Retrieve the Flower information success!", False, data=data), 200

	@staticmethod
	@authenticate
	@admin_required
	@invalidate_caches("flower")
	def post(user=None):
		"""Create a new flower"""
		parser = reqparse.RequestParser()
		parser.add_argument("flowercommonname", required=True, type=str, dest="flower_common_name")
		parser.add_argument("flowershapeid", required=True, type=str, dest="flower_shape")
		parser.add_argument("flowercolorid", required=True, type=str, dest="flower_color"),
		parser.add_argument("flowerspecies", required=True, type=str, dest="flower_species"),
		parser.add_argument("flowergenus", required=True, type=str, dest="flower_genus")
		args = parser.parse_args()
		log.info("Adding flower {}".format(args))

		engine = database.get_engine()
		query = sql.insert(database.flower).values(**args).returning(database.flower.c.flower_id)
		result = engine.execute(query)

		id = dict(next(result))
		if id is None:
			log.error("Failed to log new flower {}".format(args))
			return response("false", "Log a new flower failed", True), 405
		return response("success", "Log a new flower success!", False, data=id), 200

	@staticmethod
	@invalidate_caches("flower")
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
		engine = database.get_engine()
		query = sql.update(database.flower).values(**args).where(database.flower.c.flower_id == id).returning(database.flower.c.flower_id)
		result = engine.execute(query)

		id = dict(next(result, {}))
		if len(id) == 0:
			log.warning("Failed to update unknown flower #{}".format(id))
			return response("false", "Flower not found!", True), 404
		return response("success", "Update the Folwer information success!", False, data=id), 200  # TODO Fix typo

	@staticmethod
	@invalidate_caches("flower")
	def delete(id: int):
		"""Delete flower by ID"""
		log.info("Deleting flower {}".format(id))
		engine = database.get_engine()
		query = sql.delete(database.flower).where(database.flower.c.flower_id == id).returning(database.flower.c.flower_id)
		if next(engine.execute(query), None) is None:
			log.warning("Attempted to delete unknown flower #{}".format(id))
			return response("false", "flower id not found!", True), 404
		return response("success", "Delete flower success!", False), 200

class FlowerShapes(Resource):
	@staticmethod
	@cache_response("features")
	def get():
		"""Get all flower shapes"""
		log.debug("Retrieving list of all flower shapes")
		engine = database.get_engine()
		features = database.features
		results = engine.execute(sql.select([features]).where(features.c.feature_id.like("fc%")))
		data = [dict(r) for r in results]
		if len(data) == 0:
			log.warning("Failed to retrieve list of flower shapes")
			return response("false", "Flower shapes not found!", True), 404
		return response("success", "Retrieve the flower shapes success!", False, data=data), 200

class UnmatchedFlowers(Resource):
	@staticmethod
	@cache_response("flowerdict", "beerecord")
	def get():
		"""Get unmatched flowers"""
		log.debug("Retrieving list of unmatched flowers")
		engine = database.get_engine()
		bee = database.beerecord
		flower = database.flowerdict
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
			log.warning("Failed to retrieve list of unmatched flowers")
			return response("false", "Bee records not found!", True), 404  # TODO Change messages
		return response("success", "Retrieve the Bee records success!", False, data=data), 200

class FlowerList(Resource):
	@staticmethod
	@cache_response("flowerdict")
	def get():
		"""Legacy flowerlist endpoint"""
		log.debug("Getting list of all flowers in the flowerdict")
		engine = database.get_engine()
		results = engine.execute(sql.select([database.flowerdict]))
		data = [dict(r) for r in results]

		if len(data) == 0:
			log.error("Failed to retrieve list of flowers from the flowerdict")
			return response("false", "Flower List not found!", True), 404
		return response("success", "Retrieve the Flower List  success!", False, data=data), 200  # TODO fix typos
