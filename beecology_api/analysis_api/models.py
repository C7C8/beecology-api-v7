from flask_restx import fields

from beecology_api.analysis_api import api
from beecology_api.compat_bee_api.models import bee_vis_record


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

bi_var_request = api.inherit("Bi-variate analysis request", base_bee_data, {
	"value": fields.Nested(api.model("Variable pairs", {
		"firstTarget": fields.String(description="First variable for analysis"),
		"secondTarget": fields.String(description="Second variable analysis")
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

regression_request = api.inherit("Regression request", {
	"value": fields.Nested(api.model("Regression parameters", {
		"targetName": fields.String(description="X variable"),
		"secondTargetName": fields.String(description="Y variable"),
		"targetRange": fields.List(fields.String, description="X variable range"),
		"secondTargetRange": fields.List(fields.String, description="Y variable range")
	}))
})
