from flask_restx import fields

from .api import api
from ..common_parsers import bee_record_filter_parser

# List of all columns that appear in the dataframe that analysis scripts recieve.
df_columns = [
	"time",
	"year",
	"month",
	"day",
	"latitude",
	"longitude",
	"elevation",
	"species",
	"behavior",
	"gender",
	"tongue_length",
	"bee_active_start",
	"bee_active_end",
	"flower_species",
	"flower_genus",
	"flower_common_name",
	"flower_shape",
	"flower_bloom_start",
	"flower_bloom_end"
]

##########
# MODELS #
##########

relative_frequencies_series_element = api.model("Relative frequencies analyis series element", {
	"name": fields.String,
	"value": fields.Float
})

relative_frequencies_result = api.model("Relative frequencies analysis results", {
	"name": fields.String,
	"series": fields.List(fields.Nested(relative_frequencies_series_element))
})

###########
# PARSERS #
###########


relative_frequencies_parser = bee_record_filter_parser.copy()
relative_frequencies_parser.add_argument("x-var", type=str, help="X variable", required=True)
relative_frequencies_parser.add_argument("x-bin-cutoffs", type=float, help="List of X variable cutoffs as timestamps to bin the X axis by (at least 3) in millseconds", action="split", required=True)
relative_frequencies_parser.add_argument("y-var", type=str, help="Y variable", required=True, choices=df_columns)
relative_frequencies_parser.add_argument("norm-mode", type=str, help="Normalization mode", choices=["population", "bin"], required=False)

summary_stats_parser = bee_record_filter_parser.copy()
summary_stats_parser.add_argument("how", type=str, choices=["absolute", "relative"], required=True)
