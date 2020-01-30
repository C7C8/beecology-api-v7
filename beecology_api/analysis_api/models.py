from flask_restx import fields

from beecology_api.analysis_api import api
from beecology_api.bee_data_api.models import bee_vis_record


base_bee_data = api.model("Base bee data analysis object", {
	"beedata":  fields.List(fields.Nested(bee_vis_record), description="Bee data points to operate on"),
})

bee_data_analysis_request = api.inherit("Bee data analysis request", base_bee_data, {
	"model": fields.String(description="Model to run", required=True, enum=[
		"trend",
		"crosstab",
		"kmeans",
		"percent",
		"decisiontree",
		"linearregression",
		"nonlinear"
	]),
	"value": fields.Raw
})

trend_request = api.inherit("Trend analysis request", base_bee_data, {
	"value": fields.Nested(api.model("Trend parameters", {
		"secondTargetRange": fields.List(fields.String, description="List of values to filter the target by"),
		"secondTargetName": fields.String(description="Variable to plot trend line for")
	}))
})

cross_tabulation_request = api.inherit("Cross tabulation analysis request", base_bee_data, {
	"value": fields.Nested(api.model("Cross tabulation parameters", {
		"firstTarget": fields.String(description="First variable for cross tabulation"),
		"secondTarget": fields.String(description="Second variable for cross tabulation")
	}))
})

k_means_request = api.inherit("K means analysis request", base_bee_data, {
	"value": fields.Nested(api.model("K means parameters", {
		"numClusters": fields.Integer(description="Number of clusters"),
		"longHigh": fields.String(description="Maximum longitude to include in K-means as an integer"),
		"longLow": fields.String(description="Minimum longitude to include in K-means as an integer"),
		"latHigh": fields.String(description="Maximum latitude to include in K-means as an integer"),
		"latLow": fields.String(description="Minimum latitude to include in K-means as an integer")
	}))
})
