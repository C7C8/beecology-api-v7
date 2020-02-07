from logging import getLogger
from uuid import uuid4, UUID

from flask import request
from flask_restx import Resource, abort
from marshmallow import ValidationError
from sqlalchemy import and_

from beecology_api.beecology_api.api import reference_api as api
from beecology_api.beecology_api.db import db_session, FlowerSpecies
from beecology_api.beecology_api.serialization import flower_species_schema
from beecology_api.beecology_api.swagger import flower_species, flower_species_filter_parser

log = getLogger()

class Flower(Resource):
	@api.expect(flower_species)
	@api.response(201, "Flower species")
	@api.response(400, "Invalid request")
	def post(self):
		"""Add a new flower species"""
		# TODO Require admin auth
		api.payload["id"] = uuid4()
		with db_session() as session:
			try:
				species = flower_species_schema.load(api.payload, session=session)
			except (ValueError, ValidationError) as e:
				log.error("Flask failed to validate input to Marshmallow's standards: {}".format(api.payload), e)
				abort(400, "Invalid input")

			session.add(species)
			session.commit()

		log.info("Added new flower species {} {}".format(api.payload["genus"], api.payload["species"]))
		return {"message": "Flower species added"}, 201

	@api.param("id", "UUID of flower species to return information on")
	@api.response(200, "Species data enclosed")
	@api.response(404, "Species not found")
	def get(self, id: UUID):
		"""Get information on one flower species."""
		with db_session() as session:
			species = session.query(FlowerSpecies).filter(FlowerSpecies.id == id).first()
			if species is None:
				abort(404)
			return flower_species_schema.dump(species)

	@api.param("id", "UUID of flower species to update")
	@api.expect(flower_species)
	@api.response(204, "Species updated")
	@api.response(404, "Species not found")
	@api.response(400, "Unknown field or data type")
	def put(self, id: UUID):
		"""Update a flower species. Changes to the ID are ignored."""
		# TODO require admin auth
		api.payload["id"] = id
		with db_session() as session:
			if session.query(FlowerSpecies).filter(FlowerSpecies.id == id).first() is None:
				abort(404)

			try:
				flower_species_schema.load(api.payload, session=session)
			except (ValueError, ValidationError) as e:
				log.error("Flask failed to validate input to Marshmallow's standards: {}".format(api.payload), e)
				abort(400, "Unknown field or data type")

		session.commit()
		return "", 204

	@api.param("id", "UUID of flower species to be deleted")
	@api.response(204, "Flower species deleted (if present)")
	def delete(self, id: UUID):
		"""Delete a flower species."""
		# TODO require admin auth
		with db_session() as session:
			session.query(FlowerSpecies).filter(FlowerSpecies.id == id).delete()
			session.commit()
		return "", 204


class Flowers(Resource):
	@api.expect(flower_species_filter_parser)
	@api.response(400, "Bad filter parameters")
	@api.marshal_with(flower_species, as_list=True)
	def get(self):
		"""Get all flower species, subject to optional filtering"""
		args = flower_species_filter_parser.parse_args()
		with db_session() as session:
			query = session.query(FlowerSpecies)

			# Simple equality filtering
			for attr in  ["genus", "shape"]:
				if attr in args:
					query = query.filter(FlowerSpecies.__dict__[attr] == args[attr])

			# Months blooming filtering
			if "blooms-during" in args:
				month = args["blooms-during"]
				query = query.filter(and_(FlowerSpecies.bloom_start <= month, FlowerSpecies.bloom_end >= month))

		return [flower_species_schema.dump(species) for species in query.all()], 200
