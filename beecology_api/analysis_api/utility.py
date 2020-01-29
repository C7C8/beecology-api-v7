import json

import pandas as pd

def convert_to_dataframe(json_file):
	"""Convert bee data direct from the request to a Pandas dataframe"""
	# TODO Pandas *should* be able to convert a dict to an object directly, but frankly I'm afraid of changing this
	df = pd.read_json(json.dumps(json_file), orient='records')

	# data cleaning
	df.dropna()
	df = df[df.loc_info != "undefined"]
	df[['latitude', 'longitude']] = df['loc_info'].str.split(',', expand=True)
	df["latitude"] = pd.to_numeric(df["latitude"])
	df["longitude"] = pd.to_numeric(df["longitude"])

	df['gender'] = df['gender'].str.lower()
	df['spgender'] = df['spgender'].str.lower()
	# df['bee_name'] = df['bee_name'].str.lower()
	df['flower_name'] = df['flower_name'].str.lower()
	df['flower_color'] = df['flower_color'].str.lower()
	df['flower_shape'] = df['flower_shape'].str.lower()

	df['year'] = df['date'].dt.year
	df['month'] = df['date'].dt.month
	df['day'] = df['date'].dt.day

	return df
