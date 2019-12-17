from logging import getLogger

import sqlalchemy as sql
from flask_restplus import Resource
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
			# cursor.execute("SELECT * FROM flowerdict " + ("WHERE flower_id=%s" if id != -1 else ""), [id])
			# results = cursor.fetchall()
			fd = Database.flowerdict
			query = sql.select([fd.c.flower_id,
			                    fd.c.latin_name.label("flower_latin_name"),
			                    fd.c.main_common_name.label("flower_common_name")])
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
		return "Placeholder"

	@staticmethod
	def put():
		"""Update a flower by ID"""
		return "Placeholder"

	@staticmethod
	def delete():
		"""Delete flower by ID"""
		return "Placeholder"

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
				return response("false", "Bee records not found!", True), 404
			return response("success", "Retrieve the Bee records success!", False, data=data), 200
