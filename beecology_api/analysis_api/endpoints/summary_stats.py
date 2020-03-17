from flask_restx import Resource

from .. import api
from ..analysis_scripts import summary_stats
from ..swagger import summary_stats_parser
from ...beecology_api.endpoints.record import bee_records_filter
from ...convert_dataframe import convert_dataframe
from ...db import db_session


class SummaryStats(Resource):
	@api.expect(summary_stats_parser)
	@api.response(400, "Invalid arguments")
	@api.response(200, "Summary stats enclosed")
	def get(self):
		"""Summary stats"""
		args = summary_stats_parser.parse_args()
		with db_session() as session:
			records = bee_records_filter(args, session)
			df = convert_dataframe(records)
			return summary_stats.summary_stats(df, args["how"])
