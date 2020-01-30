from flask_restx import fields

from beecology_api.analysis_api import api
from beecology_api.bee_data_api.models import bee_vis_record


base_bee_data = api.model("Base bee data analysis object", {
	"beedata":  fields.List(fields.Nested(bee_vis_record), description="Bee data points to operate on"),
	"value": fields.Nested(api.model("Data analysis parameters", {
		"attrNames": fields.String(description="Attribute names", required=False),
		"firstTarget": fields.String(description="First target for analysis", required=False),
		"latHigh": fields.Float(90, description="Maximum latitude to filter by", required=True),
		"latLow": fields.Float(-90, description="Minimum latitude to filter by", required=True),
		"longHigh": fields.Float(180, description="Maximum longitude to filter by", required=True),
		"longLow": fields.Float(-180, description="Minimum longitude to filter by", required=True),
		"numClusters": fields.Integer(description="Number of clusters for K-Means", required=False),
		"secondTarget": fields.String(description="Second target for analysis", required=False),
		"secondTargetName": fields.String(description="Name/type of the second target", example="flower_name"),
		"secondTargetRange": fields.List(fields.String, description="List of acceptable values"),
		"targetName:": fields.String(description="Target for analysis"),
		"targetRange": fields.String,
		"yearRange": fields.List(fields.Integer, description="List of years for data to be shown from", required=True)
	}))
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
	])
})


