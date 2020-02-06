from logging import getLogger
from uuid import UUID, uuid4

from flask import request
from flask_restx import Resource, abort
from geoalchemy2 import func
from marshmallow.exceptions import ValidationError

import beecology_api.beecology_api.db as db
from beecology_api.beecology_api.api import main_api as api
from beecology_api.beecology_api.db.models import BeeRecord
from beecology_api.beecology_api.serialization import bee_record_schema
from beecology_api.beecology_api.swagger import bee_record, bee_record_filter_parser

log = getLogger()


class Record(Resource):
	@api.expect(bee_record)
	@api.response(201, "Bee record logged")
	@api.response(400, "Invalid request")
	def post(self):
		"""Log a new record. ID and username are ignored and filled in by the server."""
		# TODO require auth
		with db.db_session() as session:
			try:
				record = bee_record_schema.load(api.payload, session=session)
			except ValueError:
				log.error("Flask failed to validate input to Marshmallow's standards: {}".format(api.payload))
				abort(400, "Invalid input")

			record.id = uuid4()
			session.add(record)
			session.commit()

		return {"message": "Bee record logged"}, 201

	@api.param("id", "UUID of record to return", required=False)
	@api.response(200, "Record enclosed", bee_record)
	@api.response(404, "Record not found")
	def get(self, id: UUID):
		"""Get one bee record by ID"""
		with db.db_session() as session:
			records = session.query(BeeRecord).filter(BeeRecord.id == id).first()
			if records is None:
				abort(404)
			ret = bee_record_schema.dump(records)
			return ret

	@api.expect(bee_record)
	@api.response(204, "Bee record updated")
	@api.response(404, "Bee record not found")
	@api.response(400, "Unknown field or data type")
	@api.response(403, "Not authorized to update this record")
	def put(self, id: UUID):
		"""Update a bee record. Changes to the ID are ignored."""
		# Delete id+user-id if they exist in the payload
		with db.db_session() as session:
			record = session.query(BeeRecord).filter(BeeRecord.id == id).first()
			if record is None:
				abort(404)

			if "id" in api.payload:
				api.payload["id"] = str(id)

			try:
				record = bee_record_schema.load(api.payload, session=session)
			except (ValueError, ValidationError):
				abort(400, "Unknown field or data type")

			session.commit()
			return "", 204

	@api.response(204, "Bee record deleted")
	@api.response(403, "Not authorized to delete this record")
	def delete(self, id: UUID):
		"""Delete a bee record"""
		# TODO auth
		with db.db_session() as session:
			session.query(BeeRecord).filter(BeeRecord.id == id).delete()
			session.commit()
		return "", 204


class Records(Resource):
	@api.expect(bee_record_filter_parser)
	@api.response(400, "Bad filter parameters")
	@api.marshal_with(bee_record, as_list=True)
	def get(self):
		"""Get a list of records, filtered by any means."""
		# TODO Make sure current user is the specified user
		with db.db_session() as session:
			args = request.args
			query = session.query(BeeRecord)

			# Simple equality filtering
			for attr in ["user", "species", "flower-species", "head", "abdomen", "thorax", "city", "gender", "behavior"]:
				if attr in args:
					query = query.filter(BeeRecord.__dict__[attr] == args[attr])

			# Range or spatial -based filtering
			if "max-elevation" in args:
				query = query.filter(BeeRecord.elevation <= args["max-elevation"])
			if "min-elevation" in args:
				query = query.filter(BeeRecord.elevation >= args["min-elevation"])
			if "time-start" in args:
				query = query.filter(BeeRecord.time >= args["time-start"])
			if "time-end" in args:
				query = query.filter(BeeRecord.time <= args["time-end"])
			if "bounding-box" in args:
				# Bounding box is passed in as a list of comma-separated floats: minLat, minLong, maxLat, maxLong
				try:
					coords = [float(coord) for coord in args["bounding-box"].split(",")]
					if len(coords) != 4 or coords[0] >= coords[2] or coords[1] >= coords[3]:
						raise ValueError
				except ValueError:
					abort(400, "Invalid bounding box filter parameters")

				query = query.filter(func.ST_Within(BeeRecord.loc_info, func.ST_GeomFromText(
					"POLYGON(({0} {1}, {2} {1}, {2} {3}, {0} {3}, {0} {1}))".format(*coords))))

			ret = [bee_record_schema.dump(record) for record in query.all()], 200
			return ret
