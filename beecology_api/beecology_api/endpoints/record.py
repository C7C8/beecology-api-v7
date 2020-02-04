import uuid

from scipy.stats import geom

from beecology_api.beecology_api.api import main_api as api
import beecology_api.beecology_api.db as db
from beecology_api.beecology_api.db.models import BeeRecord
from beecology_api.beecology_api.models import bee_record
from flask_restx import Resource

class AddRecord(Resource):

	@api.expect(bee_record)
	@api.response(201, "Bee record logged")
	@api.response(400, "Invalid request")
	def post(self):
		"""Log a new record. ID and username are ignored and filled in by the server."""
		# TODO require auth
		bee = api.payload
		record = BeeRecord(
			id=uuid.uuid4(),
			name=bee["name"],
			abdomen=bee["abdomen"],
			thorax=bee["thorax"],
			time=bee["time"],
			loc_info="POINT({} {})".format(bee["loc_info"]["latitude"], bee["loc_info"]["longitude"]),
			city=bee["city"],
			gender=bee["gender"],
			behavior=bee["behavior"],
			elevation=bee["elevation"],
			images=[],
			videos=[]
		)
		session = db.Session()
		session.add(record)
		session.commit()
		session.close()

		return {"message": "Bee record logged"}, 201

class Record(Resource):
	def get(self):
		"""Get information on one or all bee records."""
		pass

	def put(self):
		"""Update a bee record."""
		pass

	def delete(self):
		"""Delete a bee record"""
		pass
