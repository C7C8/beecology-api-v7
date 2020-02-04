from flask_restx import fields

from beecology_api.beecology_api import main_api, manage_api, reference_api

_months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November",
           "December"]

gis_coordinate = main_api.model("GIS coordinate", {
	"latitude": fields.Float(description="Latitude"),
	"longitude": fields.Float(description="Longitude")
})

bee_record = main_api.model("Bee record", {
	"id": fields.String(description="UUID (v4) of the bee record", example="d667f8bc-60e5-4ea4-99b5-196c091657ac"),
	"user": fields.String(description="ID of user who submitted the record", example="wbVJ1cYguVcggk21dEkcGbnDI0Q2"),
	"bee_species_id": fields.String(description="If known, the species ID of the observed bee", example="b6567a3c-be2e-4350-b944-3ec24d868586"),
	"flower_species_id": fields.String(description="If known, the species ID of the observed flower", example="955c499b-5dd3-4521-9f75-f13b173bbc7b"),
	"name": fields.String(description="Bee name", example="Bombus impatiens"),
	"abdomen": fields.String(description="Bee abdomen type", example="a1"),
	"thorax": fields.String(description="Bee thorax type", example="f1"),
	"time": fields.DateTime(description="Time the bee record was logged"),
	"loc_info": fields.Nested(gis_coordinate, description="Point of observation"),
	"elevation": fields.Float(description="Elevation at the point the bee was observed at"),
	"city": fields.String(description="Where the bee was observed"),
	"gender": fields.String(description="Bee gender", choices=["male", "female", "either", "unknown"]),
	"behavior": fields.String(description="The bee's beehavior, i.e. what it was collecting", choices=["pollen", "nectar", "unknown"]),
	"images": fields.List(fields.String, description="List of image paths for images associated with this record"),
	"videos": fields.List(fields.String, description="List of video paths for videos associated with this record"),
})

flower_species = reference_api.model("Flower species", {
	"id": fields.String(description="UUID (v4) of the flower species", example="9c4d71a6-06a0-4aa0-9e87-428e2a77b866"),
	"genus": fields.String(description="Flower genus"),
	"species": fields.String(description="Flower species"),
	"common_name": fields.String(description="The name the flower is most often referred to by"),
	"alt_name": fields.String(description="An alternate common name for the flower"),
	"main_color": fields.String(description="The flower's dominant color"),
	"colors": fields.String(description="Comma-separated list of other colors on the flower"),
	"bloom_start": fields.String(description="When the flower species starts blooming", choices=_months),
	"bloom_end": fields.String(description="When the flower species stops blooming", choices=_months),
	"shape": fields.String(description="Flower shape"),
	"image": fields.String(description="Path to a file on this server with an image of the flower"),
})

bee_species = reference_api.model("Flower_species", {
	"id": fields.String(description="UUID (v4) of the bee species", example="57aa4241-b860-4992-992b-e827b90c0c76"),
	"genus": fields.String(description="Bee genus"),
	"species": fields.String(description="Bee species"),
	"common_name": fields.String(description="The name the bee species is most often referred to by"),
	"description": fields.String(description="Textual description of the bee in plain English"),
	"active_start": fields.String(description="When the bee species is active", choices=_months),
	"active_end": fields.String(description="When the bee species ceases activity", choices=_months),
	"confused_with": fields.String(description="Commma-separated list of bee species that this species is commonly confused with"),
	"image": fields.String(description="Path to a file on this server with an image of the bee"),
})

user = manage_api.model("User record", {
	"id": fields.String(description="User ID", example="wbVJ1cYguVcggk21dEkcGbnDI0Q2"),
	"admin": fields.Boolean(description="Whether this user is an admin or not", default=False),
	"locked": fields.Boolean(description="Whether this user's account is locked or not", default=False),
	"registered": fields.DateTime(description="When this user first registered with the server"),
	"last_login": fields.DateTime(description="The user's last login time")
})
