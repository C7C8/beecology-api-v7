from logging import getLogger

import sqlalchemy as sql
from flask_restx import Resource
from sqlalchemy import and_, func

from beecology_api import database
from beecology_api.compat_bee_api.api import api
from beecology_api.compat_bee_api.authentication import admin_required
from beecology_api.compat_bee_api.cache import invalidate_caches, cache_response
from beecology_api.compat_bee_api.models import new_flower_parser, response_wrapper, add_flower_response, \
	flower_dict_response, \
	update_flower_parser, flower_shape_response, unmatched_flowers_response, flower_list_response
from beecology_api.compat_bee_api.response import response

log = getLogger()


class Flowerdex(Resource):
	@api.expect(new_flower_parser)
	@api.response(200, "New flower added", add_flower_response)
	@api.response(405, "Failed to log new flower", response_wrapper)
	@admin_required
	@invalidate_caches("flower")
	def post(self, user=None):
		"""Create a new flower."""
		args = new_flower_parser.parse_args()
		log.info("Adding flower {}".format(args))

		engine = database.get_engine()
		query = sql.insert(database.flower).values(**args)
		id = engine.execute(query).inserted_primary_key[0]  # Not all SQL engines support RETURNING

		if id is None:
			log.error("Failed to log new flower {}".format(args))
			return response("false", "Log a new flower failed", True), 405
		return response("success", "Log a new flower success!", False, data=[{"flower_id": id}]), 200

	@api.param("id", "Optional flower ID; if not provided, all flowers are returned.", required=False)
	@api.response(200, "Flower dict entry(/entries) enclosed", flower_dict_response)
	@api.response(404, "Flower dict entry not found", response_wrapper)
	@cache_response("flowerdict")
	def get(self, id: int = -1):
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

	@api.expect(update_flower_parser)
	@api.response(200, "Updated flower", response_wrapper)
	@api.response(404, "Flower not found")
	@admin_required
	@invalidate_caches("flower")
	def put(self, id: int, user=None):
		"""Update a flower by ID"""
		args = update_flower_parser.parse_args()
		args = {k: v for k, v in args.items() if v is not None}

		log.info("Updating flower {}".format(id))
		engine = database.get_engine()
		query = sql.update(database.flower).values(**args).where(database.flower.c.flower_id == id)
		results = engine.execute(query)

		if results.rowcount == 0:
			log.warning("Failed to update unknown flower #{}".format(id))
			return response("false", "Flower not found!", True), 404
		return response("success", "Update the Folwer information success!", False, data=[{"flower_id": id}]), 200  # TODO Fix typo

	@api.response(200, "Deleted flower", response_wrapper)
	@api.response(404, "Flower ID not found", response_wrapper)
	@admin_required
	@invalidate_caches("flower")
	def delete(self, id: int, user=None):
		"""Delete flower by ID"""
		log.info("Deleting flower {}".format(id))
		engine = database.get_engine()
		query = sql.delete(database.flower).where(database.flower.c.flower_id == id)
		results = engine.execute(query)

		if results.rowcount == 0:
			log.warning("Attempted to delete unknown flower #{}".format(id))
			return response("false", "flower id not found!", True), 404
		return response("success", "Delete flower success!", False), 200


class FlowerShapes(Resource):
	@api.response(200, "List of all flower shapes enclosed", flower_shape_response)
	@api.response(404, "Failed to find any flower shapes", response_wrapper)
	@cache_response("features")
	def get(self):
		"""Get all flower shapes.

		This endpoint's name is something of a misnomer, it's more appropriately flower **features**."""
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
	@api.response(200, "List of unmatched flowers enclosed", unmatched_flowers_response)
	@api.response(404, "Didn't find any unmatched flowers", response_wrapper)
	@cache_response("flowerdict", "beerecord")
	def get(self):
		"""Get a list of recorded flowers that aren't in the flowerdex.

		List is sorted in alphabetical order by flower name."""
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
	@api.response(200, "List of all flowers enclosed", flower_list_response)
	@api.response(404, "Failed to retrieve any flowers", response_wrapper)
	@cache_response("flowerdict")
	def get(self):
		"""Legacy flowerlist endpoint"""
		log.debug("Getting list of all flowers in the flowerdict")
		engine = database.get_engine()
		results = engine.execute(sql.select([database.flowerdict]))
		data = [dict(r) for r in results]

		if len(data) == 0:
			log.error("Failed to retrieve list of flowers from the flowerdict")
			return response("false", "Flower List not found!", True), 404
		return response("success", "Retrieve the Flower List  success!", False, data=data), 200  # TODO fix typos
