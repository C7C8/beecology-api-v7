import io

import numpy as np
import pandas as pd
import pydotplus
from flask import send_file
from flask_restx import Resource
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier, export_graphviz

from beecology_api.analysis_api import api
from beecology_api.analysis_api.models import bi_var_request
from beecology_api.analysis_api.utility import convert_to_dataframe


class DecisionTree(Resource):
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

	@staticmethod
	@api.expect(bi_var_request)
	@api.response(200, "Decision tree plot")
	@api.produces(["image/png"])
	def post():
		"""Calculate a decision tree using the first target as the given and the second target as the target."""
		df = convert_to_dataframe(api.payload["beedata"])
		given = api.payload["value"]["firstTarget"]
		target = api.payload["value"]["secondTarget"]

		# TODO CLEAN THIS UP

		# Merges dataframes so that the df passed in now has tongue lengths as a column

		beechar = pd.DataFrame(DecisionTree._beecharlist, columns=['bee_name', 'tongue_length'])
		new_df = pd.merge(df, beechar, on='bee_name')

		# Convert all missing rows to unknown
		new_df = new_df.replace(np.nan, "Unknown", regex=True)

		# cut the df down to just the variables we want (ie, given & target)
		df = new_df[[given, target]]

		indexNames = df[df[target] == "Unknown"].index
		df.drop(indexNames, inplace=True)
		indexNames = df[df[given] == "Unknown"].index
		df.drop(indexNames, inplace=True)

		# One-hot encoding the data
		# especially need to one-hot the given. Dany did not one-hot encode the target, I don't know if this is correct
		# practice or not?  We will also need to test if the variables are already numeric or not
		# the only numeric vals we have are the following: year, month

		encoded_columns = df[[given]]
		encoded_columns = pd.get_dummies(encoded_columns, [given])

		merged = pd.concat([df[target], encoded_columns], axis='columns')
		# working_df = merged[~merged.flower_shape.str.contains('Unknown')]
		working_df = merged
		print(working_df)

		# Split into feature and target sets
		X = working_df.values[:, 1:]
		Y = working_df.values[:, 0]

		# Splitting data into training and test set
		X_train, X_test, y_train, y_test = train_test_split(
			X, Y, test_size=0.3, random_state=100)

		# Decision Tree Classifier w criterion entropy
		clf_entropy = DecisionTreeClassifier(criterion="entropy", random_state=100,
		                                     max_depth=20, min_samples_leaf=5)
		clf_entropy.fit(X_train, y_train)

		# Prediction for decision tree classifier with criterion as entropy
		y_pred_en = clf_entropy.predict(X_test)

		# Accuracy for decision tree classifier with criterion as entropy
		print("Accuracy is ", accuracy_score(y_test, y_pred_en) * 100)

		# METHOD 1 FOR VISUALIZATION
		dot_data = io.StringIO()

		export_graphviz(clf_entropy, out_file=dot_data,
		                filled=True, rounded=True, label='all',
		                class_names=clf_entropy.classes_,
		                feature_names=working_df.columns[1:],
		                special_characters=True)

		graph = pydotplus.graph_from_dot_data(dot_data.getvalue())
		img = io.BytesIO(graph.create_png())
		img.seek(0)

		return send_file(img, mimetype='image/png')
