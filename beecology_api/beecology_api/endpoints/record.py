import io
from logging import getLogger
from typing import List
from uuid import UUID, uuid4

from flask import send_file
from flask_jwt_extended import get_jwt_identity
from flask_restx import Resource, abort
from geoalchemy2 import func
from marshmallow.exceptions import ValidationError

from beecology_api.beecology_api.api import main_api as api
from beecology_api.beecology_api.authentication import authenticate
from beecology_api.common_parsers import bee_record_filter_parser
from beecology_api.convert_dataframe import convert_dataframe
from beecology_api.db import BeeRecord, User
from beecology_api.db import db_session
from beecology_api.db.serialization import bee_record_schema
from beecology_api.beecology_api.swagger import bee_record

log = getLogger()


class Record(Resource):
	@api.expect(bee_record)
	@api.response(201, "Bee record logged")
	@api.response(400, "Invalid request")
	@authenticate(api)
	def post(self):
		"""Log a new record. ID and username are ignored and filled in by the server."""
		api.payload["id"] = uuid4()
		api.payload["user-id"] = get_jwt_identity()
		with db_session() as session:
			try:
				record = bee_record_schema.load(api.payload, session=session)
			except (ValueError, ValidationError) as e:
				log.error("Flask failed to validate input to Marshmallow's standards: {}".format(api.payload), e)
				abort(400, "Invalid input")

			session.add(record)
			session.commit()

		return {"message": "Bee record logged"}, 201

	@api.response(200, "Record enclosed", bee_record)
	@api.response(404, "Record not found")
	def get(self, id: UUID):
		"""Get one bee record by ID"""
		with db_session() as session:
			record = session.query(BeeRecord).filter(BeeRecord.id == id).first()
			if record is None:
				abort(404)
			return bee_record_schema.dump(record)

	@api.expect(bee_record)
	@api.response(204, "Bee record updated")
	@api.response(404, "Bee record not found")
	@api.response(403, "Record update forbidden")
	@api.response(400, "Unknown field or data type")
	@authenticate(api)
	def put(self, id: UUID):
		"""Update a bee record. Updates are only allowed from users who created the request, **or** admins.
		Changes to the ID are ignored."""
		api.payload["id"] = id
		with db_session() as session:
			# Fetch the original record to make sure it exists. If the user ID doesn't match and the calling user isn't
			# an admin, disallow
			record: BeeRecord = session.query(BeeRecord).filter(BeeRecord.id == id).first()
			if record is None:
				abort(404)
			if record.user_id != get_jwt_identity():
				# Check if the user is an admin
				if not session.query(User).filter(User.id == record.user_id).first().admin:
					abort(403)

			try:
				bee_record_schema.load(api.payload, session=session)
			except (ValueError, ValidationError):
				abort(400, "Unknown field or data type")

			session.commit()
			return "", 204

	@api.response(204, "Bee record deleted (if present)")
	@api.response(403, "Record delete forbidden")
	@authenticate(api)
	def delete(self, id: UUID):
		"""Delete a bee record. The calling user must either own the record in question or be an admin."""
		with db_session() as session:
			query = session.query(BeeRecord).filter(BeeRecord.id == id)
			record: BeeRecord = query.first()
			if record.user_id != get_jwt_identity() and not session.query(User).filter(User.id == record.user_id).first().admin:
				abort(403)

			query.delete()
			session.commit()
		return "", 204


class Records(Resource):
	@api.expect(bee_record_filter_parser)
	@api.response(400, "Bad filter parameters")
	@api.marshal_with(bee_record, as_list=True)
	def get(self):
		"""Get a list of records, filtered by any means"""
		args = bee_record_filter_parser.parse_args()
		with db_session() as session:
			return [bee_record_schema.dump(record) for record in bee_records_filter(args, session)], 200


class CSVRecords(Resource):
	@api.expect(bee_record_filter_parser)
	@api.response(400, "Bad filter parameters")
	@api.response(200, "CSV enclosed")
	@api.produces(["text/csv"])
	def get(self):
		"""Get a list of records, filtered by any means in CSV format."""
		args = bee_record_filter_parser.parse_args()
		with db_session() as session:
			df = convert_dataframe(bee_records_filter(args, session), time_human_readable=True).apply(lambda x: x.fillna("Unknown") if x.dtype.kind not in 'biufc' else x)
			out = io.BytesIO()
			out.write(df.to_csv(header=True, index=False).replace('\\n', '\n').encode("utf-8"))
			out.seek(0)
			return send_file(out, mimetype="text/csv")


def bee_records_filter(args, session) -> List[BeeRecord]:
	"""Bee record filtering, encapsulated as a function so that the analysis API can use it"""
	query = session.query(BeeRecord).order_by(BeeRecord.time.desc())

	# Simple equality filtering
	for attr in ["user_id", "bee_species_id", "flower_species_id", "head_coloration", "abdomen_coloration",
	             "thorax_coloration", "closest_city", "gender", "behavior"]:
		if args[attr] is None or (type(args[attr]) is list and len(args[attr]) == 0):
			continue

		if type(args[attr]) is not list:
			query = query.filter(BeeRecord.__dict__[attr] == args[attr])
		else:
			query = query.filter(BeeRecord.__dict__[attr].in_(args[attr]))

	# Range or spatial -based filtering
	if args["max-elevation"] is not None:
		query = query.filter(BeeRecord.elevation <= args["max-elevation"])
	if args["min-elevation"] is not None:
		query = query.filter(BeeRecord.elevation >= args["min-elevation"])
	if args["time-start"] is not None:
		query = query.filter(BeeRecord.time >= args["time-start"])
	if args["time-end"] is not None:
		query = query.filter(BeeRecord.time <= args["time-end"])
	if args["bounding-box"] is not None:
		# Bounding box is passed in as a list of comma-separated floats: minLat, minLong, maxLat, maxLong
		try:
			coords = [float(coord) for coord in args["bounding-box"].split(",")]
			if len(coords) != 4 or coords[0] >= coords[2] or coords[1] >= coords[3]:
				raise ValueError
		except ValueError:
			abort(400, "Invalid bounding box filter parameters")

		query = query.filter(func.ST_Within(BeeRecord.location, func.ST_GeomFromText(
			"POLYGON(({0} {1}, {2} {1}, {2} {3}, {0} {3}, {0} {1}))".format(*coords))))

	return query.all()
