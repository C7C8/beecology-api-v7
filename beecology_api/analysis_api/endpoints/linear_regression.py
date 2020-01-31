import io

from flask import send_file
from flask_restx import Resource

import matplotlib.pyplot as plt
from sklearn import linear_model

from beecology_api.analysis_api import api
from beecology_api.analysis_api.models import regression_request
from beecology_api.analysis_api.utility import convert_to_dataframe, calc_x_y


class LinearRegression(Resource):
	@staticmethod
	@api.expect(regression_request, validate=True)
	@api.response(200, "Linear regression plot")
	@api.produces(["image/png"])
	def post():
		"""Conduct a linear regression between X/Y variables under their respective ranges"""
		args = api.payload["value"]
		df = convert_to_dataframe(api.payload["beedata"])
		x_var = args["targetName"]
		y_var = args["secondTargetName"]
		x_var_range = args["targetRange"]
		y_var_range = args["secondTargetRange"]

		print(x_var_range)
		print(df)
		plt.clf()
		reg = linear_model.LinearRegression()

		workingdf_filtered1 = calc_x_y(df, x_var, x_var_range, y_var, y_var_range)
		print(workingdf_filtered1)
		for y_el in y_var_range:
			new_el = [y_el]
			new_df_y = workingdf_filtered1[(
				workingdf_filtered1[[y_var]].isin(new_el)).all(axis=1)]
			new_df_x = new_df_y[x_var]
			print(new_df_x)
			new_df_y = new_df_y['count']
			final_df_x = []
			for el in new_df_x:
				final_df_x.append([el])
			if len(final_df_x) != 0:
				reg.fit(final_df_x, new_df_y)
				print("The R^2 value is: ")
				print(reg.score(final_df_x, new_df_y))
				print("The equation for this regression line is:")
				print('y = ' + str(reg.coef_) + 'x + ' + str(reg.intercept_))
				plt.scatter(final_df_x, new_df_y,
				            label='Observed Data for ' + y_el)
				y_pred = reg.predict(final_df_x)
				plt.plot(final_df_x, y_pred, 'r',
				         label='Predicted Line for ' + y_el)
				print()
			else:
				print("There is no data for " + y_el + " and this range")
				print()

		plt.xlabel('Year')
		plt.ylabel('Number of Observations')
		plt.title('Time versus ' + y_var)
		plt.legend(fontsize='6', title_fontsize='8', loc=2, bbox_to_anchor=(1.05, 1))
		plt.tight_layout()
		img = io.BytesIO()
		plt.savefig(img, format='png')
		img.seek(0)
		return send_file(img, mimetype='image/png', as_attachment=True, attachment_filename="linear-regression-plot.png")
