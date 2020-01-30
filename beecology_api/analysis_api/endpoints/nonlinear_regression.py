import io

import matplotlib.pyplot as plt
import numpy as np
from flask import send_file
from flask_restx import Resource
from sympy import symbols, expand

from beecology_api.analysis_api import api
from beecology_api.analysis_api.models import regression_request
from beecology_api.analysis_api.utility import convert_to_dataframe, calc_x_y


class NonlinearRegression(Resource):
	@staticmethod
	@api.expect(regression_request)
	@api.response(200, "Non linear regression plot")
	@api.produces(["image/png"])
	def post():
		"""Conduct a nonlinear regression on the two given variables"""
		args = api.payload["value"]
		df = convert_to_dataframe(api.payload["beedata"])
		x_var = args["targetName"]
		y_var = args["secondTargetName"]
		x_var_range = args["targetRange"]
		y_var_range = args["secondTargetRange"]
		degree = 2

		plt.clf()
		workingdf_filtered1 = calc_x_y(df, x_var, x_var_range, y_var, y_var_range)

		for y_el in y_var_range:
			new_el = [y_el]
			new_df_y = workingdf_filtered1[(
				workingdf_filtered1[[y_var]].isin(new_el)).all(axis=1)]
			new_df_x = new_df_y[x_var]
			new_df_y = new_df_y['count']
			if len(new_df_x) != 0:
				z = np.polyfit(new_df_x, new_df_y, degree, full=True)
				x_sym = symbols("x")
				polynomial = np.poly1d(z[0])
				res = z[1]
				print("The equation for this regression line is:")
				print(expand(polynomial(x_sym)))
				print("The residuals of the least squared fit is:")
				print(res)
				plt.scatter(new_df_x, new_df_y, label='Observed Data for ' + y_el)
				y_pred = polynomial(new_df_x)
				plt.plot(new_df_x, y_pred, 'r', label='Predicted Line for ' + y_el)
			else:
				print("There is no data for " + y_el + " and this range")
			# return "Error"

		plt.xlabel('Year')
		plt.ylabel('Number of Observations')
		plt.title('Time versus ' + y_var)
		plt.legend(fontsize='6', title_fontsize='8', loc=2, bbox_to_anchor=(1.05, 1))
		plt.tight_layout()
		img = io.BytesIO()
		plt.savefig(img, format='png')
		img.seek(0)
		return send_file(img, mimetype='image/png'), 200
