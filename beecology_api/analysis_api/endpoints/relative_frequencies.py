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
		"""Conduct a relative frequencies analysis and return the resulting data
		TODO expand docs"""
		args = relative_frequencies_parser.parse_args()
		if len(args["x-bin-cutoffs"]) < 3:
			abort(400, "x-bin-cutoffs must have at least 3 cutoffs")
		try:
			cutoffs = [pd.Timestamp(cutoff).value for cutoff in args["x-bin-cutoffs"]]
		except:
			abort(400, "x-bin-cutoffs timestamps invalid")

		# Select bee records and filter
		with db_session() as session:
			df = convert_dataframe(bee_records_filter(args, session))
		if len(df) == 0:
			abort(400, "No bee records matched filter parameters")

		results = relative_frequencies(df=df,
		                               x_var=args["x-var"],
		                               x_bin_cutoffs=cutoffs,
		                               y_var=args["y-var"],
		                               norm_mode=args["norm-mode"] if "norm-mode" in args else None)
		return results, 200
