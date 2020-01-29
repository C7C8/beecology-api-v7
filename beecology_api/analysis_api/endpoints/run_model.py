from logging import getLogger

from flask_restx import Resource

from beecology_api.analysis_api import api
from beecology_api.analysis_api.models import run_model_parser
from .crosstab import CrossTabulation
from .decisiontree import DecisionTree
from .kmeans import KMeans
from .linear_regression import LinearRegression
from .nonlinear_regression import NonlinearRegression
from .relative_percent import RelativePercent
from .trend import Trend

log = getLogger()


class RunModel(Resource):
	# Pythonic switch statement setup
	_model_routes = {
		"trend": Trend.post,
		"crosstab": CrossTabulation.post,
		"kmeans": KMeans.post,
		"percent": RelativePercent.post,
		"decisiontree": DecisionTree.post,
		"linearregression": LinearRegression.post,
		"nonlinear": NonlinearRegression.post
	}

	@api.deprecated
	@api.expect(run_model_parser)
	def post(self):
		"""Run a selected model on given data.

		This is convenience wrapper for for the different analysis endpoints, e.g. `/k-means`, provided
		for compatibility purposes. While you *can* use it, you should use the other endpoints in this
		namespace instead.<br/>

		**Important:** Each model available here has its own parameters which can't be listed here individually.
		For more information, reference the endpoints mapped to the model names below:

		| Model type | Corresponding Endpoint |
		|---|---|
		| `trend` | `/trend` |
		| `crosstab` | `/cross-tabulation` |
		| `kmeans` | `/k-means` |
		| `percent` | `/relative-percent` |
		| `decisiontree` | `/decision-tree` |
		| `linearregression` | `/linear-regression` |
		| `nonlinear` | `/nonlinear-regression` |

		These endpoint docs also specify the returns and input validation messages you can expect.
		"""
		args = run_model_parser.parse_args()
		model = args["model"]

		if model not in RunModel._model_routes:
			log.warning("User requested invalid model {}".format(model))
			return "Invalid model {} requested".format(model), 403

		return RunModel._model_routes[model]()
