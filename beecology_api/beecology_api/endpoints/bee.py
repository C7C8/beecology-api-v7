from logging import getLogger
from uuid import uuid4, UUID

from flask_restx import Resource, abort
from marshmallow import ValidationError
from sqlalchemy import and_

from beecology_api.beecology_api.api import reference_api as api
from beecology_api.beecology_api.authentication import admin_required
from beecology_api.db import db_session
from beecology_api.db.serialization import bee_species_schema, BeeSpecies
from beecology_api.beecology_api.swagger import bee_species, bee_species_filter_parser

log = getLogger()

class Bee(Resource):
	@api.expect(bee_species)
	@api.response(201, "Bee species added")
	@api.response(400, "Invalid input")
	@admin_required(api)
	def post(self):
		"""Add a new bee species"""
		api.payload["id"] = uuid4()
		with db_session() as session:
			try:
				species = bee_species_schema.load(api.payload, session=session)
			except (ValueError, ValidationError) as e:
				log.error("Flask failed to validate input to Marshmallow's standards: {}".format(api.payload), e)
				abort(400, "Invalid input")

			session.add(species)
			session.commit()

		log.info("Added new bee species {}".format(api.payload["species"]))
		return {"message": "Bee species added"}, 201

	@api.response(200, "Species data enclosed", bee_species)
	@api.response(404, "Species not found")
	@api.marshal_with(bee_species)
	def get(self, id: UUID):
		"""Get information on a single bee species."""
		with db_session() as session:
			species = session.query(BeeSpecies).filter(BeeSpecies.id == id).first()
			if species is None:
				abort(404)
			return bee_species_schema.dump(species)

	@api.expect(bee_species)
	@api.response(204, "Species updated")
	@api.response(404, "Species not found")
	@api.response(400, "Unknown field or data type")
	@admin_required(api)
	def put(self, id: UUID):
		"""Update a bee species. Changes to the ID are ignored"""
		api.payload["id"] = id
		with db_session() as session:
			if session.query(BeeSpecies).filter(BeeSpecies.id == id).first() is None:
				abort(404)

			try:
				bee_species_schema.load(api.payload, session=session)
			except (ValueError, ValidationError) as e:
				log.error("Flask failed to validate input to Marshmallow's standards: {}".format(api.payload), e)
				abort(400, "Unknown field or data type")

			session.commit()
		return "", 204

	@api.response(204, "Bee species deleted (if present)")
	@admin_required(api)
	def delete(self, id: UUID):
		"""Delete a bee species."""
		with db_session() as session:
			session.query(BeeSpecies).filter(BeeSpecies.id == id).delete()
			session.commit()
		return "", 204


class Bees(Resource):
	@api.expect(bee_species_filter_parser)
	@api.response(400, "Bad filter parameters")
	@api.marshal_with(bee_species, as_list=True)
	def get(self):
		"""Get all bee species, subject to optional filtering"""
		args = bee_species_filter_parser.parse_args()
		with db_session() as session:
			query = session.query(BeeSpecies)

			# Simple equality filtering
			for attr in ["tongue_length", "species"]:
				if  args[attr] is not None:
					args[attr] = args[attr].lower()
					query = query.filter(BeeSpecies.__dict__[attr] == args[attr])

			# Months active filtering
			if args["active-during"] is not None:
				month = args["active-during"]
				query = query.filter(and_(BeeSpecies.active_start <= month, BeeSpecies.active_end >= month))

			return [bee_species_schema.dump(species) for species in query.all()], 200
