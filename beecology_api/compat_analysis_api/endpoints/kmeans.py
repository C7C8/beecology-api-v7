import io
from datetime import datetime

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from flask import send_file
from flask_restx import Resource
from sklearn.cluster import KMeans as KMeansClustering

from beecology_api.compat_analysis_api import api
from beecology_api.compat_analysis_api.models import k_means_request
from beecology_api.compat_analysis_api.utility import convert_to_dataframe


class KMeans(Resource):
	@staticmethod
	@api.expect(k_means_request, validate=True)
	@api.response(200, "K-means plotted data")
	@api.response(500, "Not enough data selected")
	@api.produces(["image/png"])
	def post():
		"""Run k-means clustering on a given set of data"""
		args = api.payload["value"]

		df = convert_to_dataframe(api.payload["beedata"])
		time = (2009, datetime.now().year)
		lat_low = int(args["latLow"])
		lat_high = int(args["latHigh"])
		long_low = int(args["longLow"])
		long_high = int(args["longHigh"])
		num_clusters = int(args["numClusters"])

		# TODO CLEAN THIS UP!

		colors = np.array(['deepskyblue', 'steelblue', 'cornflowerblue',
		                   'royalblue', 'mediumblue', 'navy'])
		colors = colors[:num_clusters]

		# filter bad values out
		df = df.dropna()
		df = df[df.longitude != 1000]
		df = df[df.latitude != 1000]

		# filter it so that it includes approx. MA, CT, and RI
		df_area = df[df['longitude'].between(long_low, long_high, inclusive=True)]
		df_area = df_area[df['latitude'].between(lat_low, lat_high, inclusive=True)]

		# filter it to be a certain time range
		df_time = df_area[df_area['year'].between(
			min(time), max(time), inclusive=True)]

		# filter the elevation to be low or high
		# this is not currently how the data is storing elevation nor is the data storing elevation, so we cannot do this.
		#     if elevation == 'low':
		#         df_elev = df_time[df_time['altitude'].isin(['low'])]
		#     if elevation == 'high':
		#         df_elev = df_time[df_time['altitude'].isin(['high'])]
		#     else:
		#         df_elev = df_time

		def_clustering = KMeansClustering(n_clusters=num_clusters, random_state=0)
		X = df_time[['longitude', 'latitude']]
		clusters = def_clustering.fit(X)
		centers = clusters.cluster_centers_
		ykmeans = clusters.predict(X)
		plt.clf()
		plt.scatter(df_time['longitude'], df_time['latitude'],
		            c=colors[pd.Series(ykmeans)], s=50)
		plt.scatter(centers[:, 0], centers[:, 1], c='salmon', s=50, alpha=.75)
		plt.title("K-Means Clustering with clusters n=" + str(num_clusters))
		plt.xlabel("Longitude")
		plt.ylabel("Latitude")
		plt.xlim(-73.7, -69.7)
		plt.ylim(40.9, 43.5)
		print("These are the centers of the clusters")
		print(centers)
		img = io.BytesIO()
		plt.savefig(img, format='png')
		img.seek(0)
		return send_file(img, mimetype='image/png', as_attachment=True, attachment_filename="k-means-plot.png")
