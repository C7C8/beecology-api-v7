import io

import pandas as pd
from flask import send_file
from flask_restx import Resource

import matplotlib.pyplot as plt
import seaborn as sns

from beecology_api.compat_analysis_api import api
from beecology_api.compat_analysis_api.models import base_bee_data
from beecology_api.compat_analysis_api.utility import convert_to_dataframe


class RelativePercent(Resource):
	@staticmethod
	@api.expect(base_bee_data, validate=True)
	@api.response(200, "Relative percent occurrence of bees line plot")
	@api.produces(["image/png"])
	def post():
		"""Get a graph of relative bee occurrence per by year, as percents.

		This endpoint endpoint does not actually require any parameters beyond data, somehow."""

		df = convert_to_dataframe(api.payload["beedata"])
		y_var = "bee_name"
		year_range = ('Bombus vagans', 'Bombus impatiens', 'Bombus fervidus', 'Bombus griseocollis')  # What?!

		# TODO CLEAN THIS UP
		first_filtered_df = df[(df[['year']].isin(year_range)).all(axis=1)]
		overall_df_percent = pd.DataFrame(columns={'year', y_var, 'percent'})
		new_year_range = year_range
		for year in year_range:
			second_filtered_df = df[(df[['year']].isin([year])).all(axis=1)]
			frequencies_yr = second_filtered_df[y_var].value_counts()
			frequencies_yr = frequencies_yr.sort_index()
			df.loc[:, "bee_name"].mode()
			percentages_yr = frequencies_yr / len(second_filtered_df)
			year_arr = []
			for i in range(len(percentages_yr)):
				year_arr.append(year)
			percentages_df = pd.DataFrame(
				{'year': year_arr, y_var: percentages_yr.index, 'percent': percentages_yr.values})
			overall_df_percent = overall_df_percent.append(
				percentages_df, ignore_index=True, sort=True)
		df = overall_df_percent

		plt.clf()
		new_plot = sns.scatterplot(x='year', y='percent', hue=y_var, data=df)
		new_plot.set_title("Time VS " + y_var)
		second_plot = sns.lineplot(x='year', y='percent', hue=y_var, data=df)
		plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
		img = io.BytesIO()
		plt.savefig(img, format='png')
		img.seek(0)
		return send_file(img, mimetype='image/png', as_attachment=True, attachment_filename="relative-percent-plot.png")
