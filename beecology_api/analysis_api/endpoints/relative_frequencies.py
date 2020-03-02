import pandas as pd
from flask import send_file

from flask_restx import Resource, abort

from beecology_api.analysis_api.analysis_scripts import relative_frequencies
from beecology_api.analysis_api.api import api
from beecology_api.db import db_session
from beecology_api.swagger import bee_record_filter_parser
from beecology_api.beecology_api.endpoints.record import bee_records_filter


relative_frequencies_parser = bee_record_filter_parser.copy()
relative_frequencies_parser.add_argument("x-var", type=str, help="X variable", required=True)
relative_frequencies_parser.add_argument("x-bin-cutoffs", type=str, help="List of X variable cutoffs as timestamps to bin the X axis by (at least 3)", action="split", required=True)
relative_frequencies_parser.add_argument("y-var", type=str, help="Y variable", required=True)
relative_frequencies_parser.add_argument("norm-mode", type=str, help="Normalization mode", choices=["population", "bin"], required=False)

class RelativeFrequencies(Resource):
	@api.expect(relative_frequencies_parser)
	@api.response(200, "Relative frequencies plot enclosed")
	@api.response(400, "Bad parameters supplied")
	def get(self):
		"""Conduct a relative frequencies analysis and return the resulting plot as a PNG.
		TODO expand docs"""
		args = relative_frequencies_parser.parse_args()
		if len(args["x-bin-cutoffs"]) < 3:
			abort(400, "x-bin-cutoffs must have at least 3 cutoffs")
		try:
			cutoffs = [pd.Timestamp(cutoff) for cutoff in args["x-bin-cutoffs"]]
		except:
			abort(400, "x-bin-cutoffs timestamps invalid")

		# Select bee records and filter
		with db_session() as session:
			records = bee_records_filter(args, session)
		if len(records) == 0:
			abort(400, "No bee records matched filter parameters")

		df = pd.DataFrame([obj.__dict__ for obj in records])
		df.to_pickle("example_df.pkl")
		image_binary = relative_frequencies(df=df,
		                                    x_var=args["x-var"],
		                                    x_bin_cutoffs=cutoffs,
		                                    y_var=args["y-var"],
		                                    norm_mode=args["norm-mode"] if "norm-mode" in args else None)
		return send_file(image_binary, mimetype='image/png', as_attachment=True, attachment_filename="relative_frequencies.png")
