from logging import getLogger
from uuid import uuid4, UUID

from flask_restx import Resource, abort
from marshmallow import ValidationError
from sqlalchemy import and_

from beecology_api.beecology_api.api import reference_api as api
from beecology_api.beecology_api.authentication import admin_required
from beecology_api.beecology_api.endpoints.record import bee_records_filter
from beecology_api.common_parsers import bee_record_filter_parser
from beecology_api.db import db_session, FlowerSpecies
from beecology_api.db.serialization import flower_species_schema
from beecology_api.beecology_api.swagger import flower_species, flower_species_filter_parser, flower_distinct_values

log = getLogger()

class Flower(Resource):
	@api.expect(flower_species)
	@api.response(201, "Flower species")
	@api.response(400, "Invalid request")
	@admin_required(api)
	def post(self):
		"""Add a new flower species"""
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

	@api.response(200, "Species data enclosed")
	@api.response(404, "Species not found")
	@api.marshal_with(flower_species)
	def get(self, id: UUID):
		"""Get information on one flower species."""
		with db_session() as session:
			species = session.query(FlowerSpecies).filter(FlowerSpecies.id == id).first()
			if species is None:
				abort(404)
			return flower_species_schema.dump(species)

	@api.expect(flower_species)
	@api.response(204, "Species updated")
	@api.response(404, "Species not found")
	@api.response(400, "Unknown field or data type")
	@admin_required(api)
	def put(self, id: UUID):
		"""Update a flower species. Changes to the ID are ignored."""
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

	@api.response(204, "Flower species deleted (if present)")
	@admin_required(api)
	def delete(self, id: UUID):
		"""Delete a flower species."""
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
			for attr in ["genus", "species", "shape"]:
				if args[attr] is None or (type(args[attr]) is list and len(args[attr]) == 0):
					continue

				if type(args[attr]) is not list:
					query = query.filter(Flower.__dict__[attr] == args[attr])
				else:
					query = query.filter(Flower.__dict__[attr].in_(args[attr]))

			# Months blooming filtering
			if args["blooms-during"] is not None:
				month = args["blooms-during"]
				query = query.filter(and_(FlowerSpecies.bloom_start <= month, FlowerSpecies.bloom_end >= month))

			return [flower_species_schema.dump(species) for species in query.all()], 200


class FlowerDistinctValues(Resource):
	@api.expect(bee_record_filter_parser)
	@api.response(200, "Distinct flower values in-use enclosed", flower_distinct_values)
	def get(self):
		"""Returns lists of possible flower names, shapes, and colors, but only for those flowers that actually appear in bee records"""
		with db_session() as session:
			args = bee_record_filter_parser.parse_args()
			records = bee_records_filter(args, session)

			flowers = set()
			colors = set()
			shapes = set()
			for record in records:
				if record.flower_species is None:
					continue
				flower = record.flower_species
				flowers.add(flower)
				colors.update(flower.colors)
				shapes.add(flower.shape)

			flowers = [flower_species_schema.dump(flower) for flower in flowers]
			return {
				"shapes": list(shapes),
				"colors": list(colors),
				"flowers": flowers
			}

