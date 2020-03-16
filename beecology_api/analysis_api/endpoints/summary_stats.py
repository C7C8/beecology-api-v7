from flask_restx import Resource

from .. import api
from ..swagger import summary_stats_parser


class SummaryStats(Resource):
	@api.expect(summary_stats_parser)
	@api.response(400, "Invalid arguments")
	@api.response(200, "Summary stats enclosed")
	def get(self):
		"""Summary stats, unimplemented at the moment"""
		pass
