import pandas as pd
from flask_restx import Resource

from beecology_api.analysis_api import api
from beecology_api.analysis_api.models import bi_var_request
from beecology_api.analysis_api.utility import convert_to_dataframe


class CrossTabulation(Resource):
	_beecharlist = [['Bombus affinis', 'short'],
	               ['Bombus bimaculatus', 'long'],
	               ['Bombus borealis', 'long'],
	               ['Bombus fervidus', 'long'],
	               ['Bombus griseocollis', 'med'],
	               ['Bombus impatiens', 'med'],
	               ['Bombus pensylvanicus', 'long'],
	               ['Bombus perplexus', 'med'],
	               ['Bombus ternarius', 'short'],
	               ['Bombus terricola', 'short'],
	               ['Bombus vagans', 'long']]
	_beechar = pd.DataFrame(_beecharlist, columns=['bee_name', 'tongue_length'])

	@staticmethod
	@api.expect(bi_var_request, validate=True)
	@api.response(200, "Cross-tabulation of two variables, given as a tab-separated table.")
	@api.produces(["text/plain"])
	def post():
		"""Calculate a cross tabulation between two provided """
		data = convert_to_dataframe(api.payload["beedata"])
		choice2 = api.payload["value"]["firstTarget"]
		choice1 = api.payload["value"]["secondTarget"]

		data_new = pd.merge(data, CrossTabulation._beechar, on='bee_name')

		# calculate the crosstab using the new dataframe
		cross: pd.DataFrame = pd.crosstab(data_new[choice1], data_new[choice2])

		# return the crosstab
		return cross.to_string()

