import io

import matplotlib.pyplot as plt
import seaborn as sns
from flask import send_file
from flask_restx import Resource

from beecology_api.compat_analysis_api import api
from beecology_api.compat_analysis_api.models import trend_request
from beecology_api.compat_analysis_api.utility import convert_to_dataframe


class Trend(Resource):
	@staticmethod
	@api.expect(trend_request, validate=True)
	@api.response(200, "Trend line plot as PNG")
	@api.produces(["image/png"])
	def post():
		"""Get a trendline plot for a given variable over time"""

		# TODO CLEAN THIS UP!

		df = convert_to_dataframe(api.payload["beedata"])
		y_var_range = api.payload["value"]["secondTargetRange"]
		y_var = api.payload["value"]["secondTargetName"]
		year_range = list(range(2010, 2020))

		workingseries = df.groupby(['year', y_var]).size()
		workingdf = workingseries.reset_index()
		workingdf.columns = ['year', y_var, 'count']
		workingdf_filtered1 = workingdf[(
			workingdf[['year']].isin(year_range)).all(axis=1)]
		workingdf_filtered2 = workingdf_filtered1[(
			workingdf_filtered1[[y_var]].isin(y_var_range)).all(axis=1)]
		workingdf_filtered2 = workingdf_filtered2.sort_values(by='year')
		plt.clf()
		workingplot = sns.lineplot(
			x='year', y='count', hue=y_var, data=workingdf_filtered2, sort=True)
		workingplot.set_title("Time VS " + y_var)
		plt.legend(fontsize='6', title_fontsize='8', loc=2, bbox_to_anchor=(1.05, 1))
		plt.tight_layout()
		img = io.BytesIO()
		fig = workingplot.get_figure()
		fig.savefig(img, format='png')
		img.seek(0)
		return send_file(img, mimetype='image/png', as_attachment=True, attachment_filename="trendplot.png")
