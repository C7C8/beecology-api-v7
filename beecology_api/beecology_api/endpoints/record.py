import uuid
from logging import getLogger

from flask import jsonify
from flask_restx import Resource, fields

import beecology_api.beecology_api.db as db
from beecology_api.beecology_api.api import main_api as api
from beecology_api.beecology_api.db.models import BeeRecord
from beecology_api.beecology_api.swagger import bee_record
from beecology_api.beecology_api.serialization import bee_record_schema

logger = getLogger()


class Record(Resource):
	@api.expect(bee_record)
	@api.response(201, "Bee record logged")
	@api.response(400, "Invalid request")
	def post(self):
		"""Log a new record. ID and username are ignored and filled in by the server."""
		# TODO require auth
		session = db.Session()
		try:
			record = bee_record_schema.load(api.payload, session=session)
		except ValueError:
			return {"message": "Invalid input"}, 400

		record.id = uuid.uuid4()

		session.add(record)
		session.commit()
		session.close()

		return {"message": "Bee record logged"}, 201

	@api.param("id", "UUID of record to return", required=False)
	@api.response(200, "Record enclosed", bee_record)
	@api.response(404, "Record not found")
	def get(self, id: uuid.UUID):
		"""Get one bee record by ID"""
		session = db.Session()
		records = session.query(BeeRecord).filter(BeeRecord.id == id).first()
		if records is None:
			return {"message": "ID {} not found".format(id)}, 404
		return jsonify(bee_record_schema.dump(records[0]))

	def put(self):
		"""Update a bee record."""
		pass

	def delete(self):
		"""Delete a bee record"""
		pass


class Records(Resource):
	@api.response(400, "Nonsensical filter parameters provided")
	@api.marshal_with(bee_record, as_list=True)
	def get(self):
		"""Get a list of records, filtered by any means."""
		session = db.Session()
		records = session.query(BeeRecord).all()
		records = [bee_record_schema.dump(record) for record in records]
		return jsonify(records)
