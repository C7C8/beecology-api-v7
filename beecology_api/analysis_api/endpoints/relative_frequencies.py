import pandas as pd
from flask_restx import Resource, abort

from beecology_api.analysis_api.analysis_scripts import relative_frequencies
from beecology_api.analysis_api.api import api
from beecology_api.analysis_api.swagger import relative_frequencies_result, relative_frequencies_parser
from beecology_api.beecology_api.endpoints.record import bee_records_filter
from beecology_api.convert_dataframe import convert_dataframe
from beecology_api.db import db_session


class RelativeFrequencies(Resource):
	@api.expect(relative_frequencies_parser)
	@api.response(400, "Bad parameters supplied")
	@api.marshal_with(relative_frequencies_result, as_list=True)
	def get(self):
		"""Conduct a relative frequencies analysis and return the resulting data"""
		args = relative_frequencies_parser.parse_args()
		if len(args["x-bin-cutoffs"]) < 2:
			abort(400, "x-bin-cutoffs must have at least 2 cutoffs")

		if args["x-var"] == "time":
			try:
				cutoffs = [int(cutoff) for cutoff in args["x-bin-cutoffs"]]
				cutoffs.sort()
			except Exception as e:
				abort(400, "x-bin-cutoffs timestamps invalid: {}".format(e))
		else:
			cutoffs = args["x-bin-cutoffs"]

		# Select bee records and filter
		with db_session() as session:
			df = convert_dataframe(bee_records_filter(args, session).all())
		if len(df) == 0:
			abort(400, "No bee records matched filter parameters")

		try:
			return relative_frequencies(df=df,
		                               x_var=args["x-var"],
		                               x_bin_cutoffs=cutoffs,
		                               y_var=args["y-var"],
		                               norm_mode=args["norm-mode"]), 200
		except ValueError as e:
			abort(400, "Binning error: {}".format(e))
