from flask_restx.reqparse import RequestParser

###############
# DATA MODELS #
###############


###################
# RESPONSE MODELS #
###################


###########
# PARSERS #
###########

run_model_parser = RequestParser()
run_model_parser.add_argument("model", type=str, required=True, help="Model to run", choices=[
	"trend",
	"crosstab",
	"kmeans",
	"percent",
	"decisiontree",
	"linearregression",
	"nonlinear"
])
run_model_parser.add_argument("beedata", type=str, required=True, help="Bee data")

trend_model_parser = RequestParser()
# run_model_parser.add_argument("beedata", type=str, required=True, help="Bee data")
