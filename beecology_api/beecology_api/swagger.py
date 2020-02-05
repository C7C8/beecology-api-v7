from datetime import datetime
from uuid import UUID

from flask_restx import fields, reqparse, inputs

from beecology_api.beecology_api import main_api, manage_api, reference_api
from .db import beehaviors, months, genders

_uuid_pattern = "[0-9a-fA-F]{8}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{12}"


##########
# MODELS #
##########

gis_coordinate = main_api.model("GIS coordinate", {
	"latitude": fields.Float(description="Latitude"),
	"longitude": fields.Float(description="Longitude")
})

bee_record = main_api.model("Bee record", {
	"id": fields.String(description="UUID (v4) of the bee record", example="d667f8bc-60e5-4ea4-99b5-196c091657ac", pattern=_uuid_pattern),
	# "user": fields.String(description="ID of user who submitted the record", example="wbVJ1cYguVcggk21dEkcGbnDI0Q2"),
	"bee_species_id": fields.String(description="If known, the species ID of the observed bee", example="b6567a3c-be2e-4350-b944-3ec24d868586", pattern=_uuid_pattern, required=False),
	"flower_species_id": fields.String(description="If known, the species ID of the observed flower", example="955c499b-5dd3-4521-9f75-f13b173bbc7b", pattern=_uuid_pattern, required=False),
	"name": fields.String(description="Bee name", example="Bombus impatiens"),
	"abdomen": fields.String(description="Bee abdomen type", example="a1", required=True),
	"thorax": fields.String(description="Bee thorax type", example="f1", required=True),
	"time": fields.DateTime(description="Time the bee record was logged", required=True),
	"loc_info": fields.Nested(gis_coordinate, description="Point of observation", required=True),
	"elevation": fields.Float(description="Elevation at the point the bee was observed at"),
	"city": fields.String(description="Where the bee was observed"),
	"gender": fields.String(description="Bee gender", enum=genders, required=True),
	"behavior": fields.String(description="The bee's beehavior, i.e. what it was collecting", enum=beehaviors, required=True),
	"images": fields.List(fields.String, description="List of image paths for images associated with this record", required=True),
	"videos": fields.List(fields.String, description="List of video paths for videos associated with this record"),
})

flower_species = reference_api.model("Flower species", {
	"id": fields.String(description="UUID (v4) of the flower species", example="9c4d71a6-06a0-4aa0-9e87-428e2a77b866", pattern=_uuid_pattern),
	"genus": fields.String(description="Flower genus", required=True),
	"species": fields.String(description="Flower species", required=True),
	"common_name": fields.String(description="The name the flower is most often referred to by", required=True),
	"alt_name": fields.String(description="An alternate common name for the flower", required=True),
	"main_color": fields.String(description="The flower's dominant color", required=True),
	"colors": fields.String(description="Comma-separated list of other colors on the flower"),
	"bloom_start": fields.String(description="When the flower species starts blooming", enum=months, required=True),
	"bloom_end": fields.String(description="When the flower species stops blooming", enum=months, required=True),
	"shape": fields.String(description="Flower shape"),
	"image": fields.String(description="Path to a file on this server with an image of the flower"),
})

bee_species = reference_api.model("Flower_species", {
	"id": fields.String(description="UUID (v4) of the bee species", example="57aa4241-b860-4992-992b-e827b90c0c76", pattern=_uuid_pattern),
	"genus": fields.String(description="Bee genus", required=True),
	"species": fields.String(description="Bee species", required=True),
	"common_name": fields.String(description="The name the bee species is most often referred to by", required=True),
	"description": fields.String(description="Textual description of the bee in plain English", required=True),
	"active_start": fields.String(description="When the bee species is active", enum=months, required=True),
	"active_end": fields.String(description="When the bee species ceases activity", enum=months, required=True),
	"confused_with": fields.String(description="Commma-separated list of bee species that this species is commonly confused with"),
	"image": fields.String(description="Path to a file on this server with an image of the bee", required=True),
})

user = manage_api.model("User record", {
	"id": fields.String(description="User ID", example="wbVJ1cYguVcggk21dEkcGbnDI0Q2", required=True),
	"admin": fields.Boolean(description="Whether this user is an admin or not", default=False, required=True),
	"locked": fields.Boolean(description="Whether this user's account is locked or not", default=False, required=True),
	"registered": fields.DateTime(description="When this user first registered with the server", required=True),
	"last_login": fields.DateTime(description="The user's last login time", required=True)
})

###########
# PARSERS #
###########

bee_record_filter_parser = reqparse.RequestParser()
bee_record_filter_parser.add_argument("user", type=str, help="User ID. Only works if the current user is the one given by the ID.", required=False)
bee_record_filter_parser.add_argument("species", type=str, help="Species UUID", required=False)
bee_record_filter_parser.add_argument("flower-species", type=str, help="Flower species UUID", required=False),
bee_record_filter_parser.add_argument("abdomen", type=str, help="Abdomen type", required=False)
bee_record_filter_parser.add_argument("thorax", type=str, help="Thorax type", required=False)
bee_record_filter_parser.add_argument("time-start", type=inputs.datetime, help="Time that records must fall at or after", required=False)
bee_record_filter_parser.add_argument("time-end", type=inputs.datetime, help="Time that records must fall at or before", required=False)
bee_record_filter_parser.add_argument("city", type=str, help="City that records must be located in", required=False)
bee_record_filter_parser.add_argument("gender", type=str, help="Bee gender", choices=genders, required=False)
bee_record_filter_parser.add_argument("behavior", type=str, help="Bee beehavior", choices=beehaviors, required=False)
bee_record_filter_parser.add_argument("max-elevation", type=float, help="Elevation that records must be at or below", required=False)
bee_record_filter_parser.add_argument("min-elevation", type=float, help="Elevation that records must be at or above", required=False)
bee_record_filter_parser.add_argument("bounding-box", type=str, help="Bounding box that records must fall in, in format minLat,minLong,maxLat,maxLong", required=False)
