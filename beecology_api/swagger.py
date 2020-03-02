from flask_restx import fields, reqparse, inputs

from beecology_api.beecology_api import main_api, manage_api, reference_api
from beecology_api.db import beehaviors, months, genders, news_types

_uuid_pattern = "[0-9a-fA-F]{8}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{12}"


##########
# MODELS #
##########

gis_coordinate = main_api.model("GIS coordinate", {
	"latitude": fields.Float(description="Latitude"),
	"longitude": fields.Float(description="Longitude")
})

media = main_api.model("Media information", {
	"id": fields.String(description="UUID (v1) for the media", pattern=_uuid_pattern, required=True),
	"path": fields.String(description="File path to the media on this server", required=False),
	"uploaded": fields.DateTime(description="When the image was uploaded to the server", required=False)
})

bee_record = main_api.model("Bee record", {
	"id": fields.String(description="UUID (v4) of the bee record", example="d667f8bc-60e5-4ea4-99b5-196c091657ac", pattern=_uuid_pattern),
	# "user": fields.String(description="ID of user who submitted the record", example="wbVJ1cYguVcggk21dEkcGbnDI0Q2"),
	"bee_species_id": fields.String(description="If known, the species ID of the observed bee", example="b6567a3c-be2e-4350-b944-3ec24d868586", pattern=_uuid_pattern, required=False),
	"flower_species_id": fields.String(description="If known, the species ID of the observed flower", example="955c499b-5dd3-4521-9f75-f13b173bbc7b", pattern=_uuid_pattern, required=False),
	"bee_name": fields.String(description="Bee name", example="Bombus impatiens", required=False),
	"abdomen_coloration": fields.String(description="Bee abdomen type", example="a1", required=True),
	"thorax_coloration": fields.String(description="Bee thorax type", example="f1", required=True),
	"head_coloration": fields.String(description="Bee head type", example="h1", required=True),
	"gender": fields.String(description="Bee gender", enum=genders, required=True),
	"behavior": fields.String(description="The bee's beehavior, i.e. what it was collecting", enum=beehaviors, required=True),
	"time": fields.DateTime(description="Time the bee record was logged", required=True),
	"submitted": fields.DateTime(decription="Time the bee record was submitted", required=False),
	"location": fields.Nested(gis_coordinate, description="Point of observation", required=True),
	"elevation": fields.Float(description="Elevation at the point the bee was observed at", required=False),
	"closest_city": fields.String(description="Where the bee was observed", required=False),
	"images": fields.List(fields.String, description="List of images associated with this record", required=True),
	"videos": fields.List(fields.String, description="List of video paths for videos associated with this record", required=False),
	"app_version": fields.String(description="App version that submitted the log", required=True)
})

flower_species = reference_api.model("Flower species", {
	"id": fields.String(description="UUID (v4) of the flower species", example="9c4d71a6-06a0-4aa0-9e87-428e2a77b866", pattern=_uuid_pattern),
	"genus": fields.String(description="Flower genus", required=True),
	"species": fields.String(description="Flower species", required=True),
	"common_name": fields.String(description="The name the flower is most often referred to by", required=True),
	"alt_names": fields.List(fields.String, description="An alternate common name for the flower", required=False),
	"main_color": fields.String(description="The flower's dominant color", required=True),
	"colors": fields.List(fields.String, description="List of other colors on the flower"),
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
	"email": fields.String(description="User email", required=False),
	"admin": fields.Boolean(description="Whether this user is an admin or not", default=False, required=True),
	"locked": fields.Boolean(description="Whether this user's account is locked or not", default=False, required=True),
	"registered": fields.DateTime(description="When this user first registered with the server", required=True),
	"last_login": fields.DateTime(description="The user's last login time", required=True)
})

news_item = manage_api.model("News item", {
	"type": fields.String(description="Type or category of news", enum=news_types),
	"posted": fields.DateTime(description="When the news was posted"),
	"content": fields.Raw(description="Arbitrary news content as a regular JSON object (not a string)")
})

jwt_response = manage_api.model("JWT", {
	"access_token": fields.String,
	"refresh_token": fields.String,
	"expires": fields.DateTime
})

###########
# PARSERS #
###########

bee_record_filter_parser = reqparse.RequestParser()
bee_record_filter_parser.add_argument("user", type=str, help="User ID. Only works if the current user is the one given by the ID.", required=False)
bee_record_filter_parser.add_argument("species", type=str, help="Species UUID", required=False)
bee_record_filter_parser.add_argument("flower-species", type=str, help="Flower species UUID", required=False),
bee_record_filter_parser.add_argument("head", type=str, help="Head type", required=False)
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

bee_species_filter_parser = reqparse.RequestParser()
bee_species_filter_parser.add_argument("genus", type=str, help="Bee genus", required=False)
bee_species_filter_parser.add_argument("tongue-length", type=str, help="Bee tongue length", required=False)
bee_species_filter_parser.add_argument("active-during", type=str, help="Month that the bee must be active during", choices=months, required=False)

flower_species_filter_parser = reqparse.RequestParser()
flower_species_filter_parser.add_argument("genus", type=str, help="Flower genus", required=False)
flower_species_filter_parser.add_argument("shape", type=str, help="Flower shape", required=False)
flower_species_filter_parser.add_argument("blooms-during", type=str, help="Month in which the flower must be in bloom", choices=months, required=False)

media_upload_parser = reqparse.RequestParser()
media_upload_parser.add_argument("data", type=str, help="Base 64 encoded media", required=True)

news_filter_parser = reqparse.RequestParser()
news_filter_parser.add_argument("type", type=str, help="News type to fetch", choices=news_types, required=False)
news_filter_parser.add_argument("before", type=str, help="Filter by date posted: entries posted on or before given date")
news_filter_parser.add_argument("after", type=str, help="Filter by date posted: entries posted on or after given date")
