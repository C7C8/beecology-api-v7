from flask_restx import reqparse, fields

from beecology_api.bee_data_api.api import api

###############
# DATA MODELS #
###############

bee_record_no_elevation = api.model("Bee record (no elevation)", {
    "beerecord_id": fields.Integer(min=0),
    "user_id": fields.String(description="User ID string"),
    "bee_dict_id": fields.Integer(description="A bee dictionary ID. Due to a bug in the old Node server , many of these"
                                              " IDs are the year the record was submitted."),
    "bee_name": fields.String(description="Latin bee genus+species designation"),
    "coloration_head": fields.String(description="Head coloration as defined by enumeration", max_length=2, example="h2"),
    "coloration_abdomen": fields.String(description="Abdomen coloration as defined by enumeration", max_length=2, example="a1"),
    "coloration_thorax": fields.String(description="Thorax coloration as defined by enumeration", max_length=2, example="t2"),
    "gender": fields.String(description="Gender of bee", enum=["Male", "Female", "Male/Female", "Unknown"]),
    "flower_name": fields.String(description="Latin flower genus+species designation"),
    "city_name": fields.String,
    "flower_shape": fields.String,
    "flower_color": fields.String(description="Plain English word for flower color"),
    "loc_info": fields.String(description="Comma-delimited latitude+longitude coordinates", example="42.59, -71.70"),
    "date": fields.DateTime(dt_format="%Y-%m-%dT%H:%M:%S.%fZ"),
    "bee_behavior": fields.String(description="What the bee is collecting", enum=["pollen", "nectar", "unknown"]),
    "record_pic_path": fields.String(description="File path under this server to image associated with this record"),
    "record_video_path": fields.String(description="Unused. Currently left blank.")
})

bee_record = api.inherit("Bee record", bee_record_no_elevation, {
    "elevation": fields.String(description="Elevation in feet. Yes, this is actually an integer in string format.", example="129")
})

bee_record_extended = api.inherit("Bee record (extended)", bee_record, {
    "app_version": fields.String(description="Application version", pattern="("),
    "common_name": fields.String(description="Flower common English name")
})

bee_vis_record = api.model("Bee vis record", {
    "bee_name": fields.String(description="Latin bee genus+species designation"),
    "date": fields.DateTime(dt_format="%Y-%m-%dT%H:%M:%S.%fZ"),
    "loc_info": fields.String(description="Comma-delimited latitude+longitude coordinates", example="42.59, -71.70"),
    "elevation": fields.String(description="Elevation in feet. Yes, this is actually an integer in string format.",
                               example="129"),
    "flower_name": fields.String(description="Plain English flower name"),
    "flower_shape": fields.String,
    "flower_color": fields.String(description="Plain English word for flower color"),
    "bee_behavior": fields.String(description="What the bee is collecting", enum=["pollen", "nectar", "unknown"]),
    "gender": fields.String(description="Gender of bee", enum=["Male", "Female", "Male/Female", "Unknown"]),
    "spgender": fields.String(description="Gender of bee", enum=["Male", "Female", "Male/Female", "Unknown"]),
})

beedex_entry = api.model("BeeDex entry", {
    "bee_id": fields.Integer,
    "bee_name": fields.String(description="Latin genus+species bee designation", example="Bombus griseocollis"),
    "common_name": fields.String(description="Plain English bee name", example="Brown-belted bumble bee"),
    "description": fields.String(description="Visual description of the bee", example="This bumble bee has a black dot on the thorax, is dark around the wings and has a thin orange band before the abdomen becomes mostly black."),
    "active_months": fields.String(description="Range of months a bee species is active in", example="May - October"),
    "confused": fields.String(description="Comma-separated list of species the bee is often confused with", example="bimaculatus, affinis, impatiens"),
    "bee_pic_path": fields.String(description="File path under this server to a picture of the bee"),
    "abdomen_list": fields.String(description="List of abdomens associated with this bee. Usually null.", example='{"a3", "a13"}'),
    "thorax list": fields.String(description="List of thoraxes associated with this bee. Usually null.", example='{"t1", "t1"}'),
    "head_list": fields.String(description="List of heads associated with this bee. Usually null.", example='{"h2", "h3"}')
})

user_access_token = api.model("Access token", {
    "accessToken": fields.String(description="Access token, a JWT used as bearer token for authentication."),
    "expiresIn": fields.Integer(3600000, description="Milliseconds until token expiration"),
    "expiresAt": fields.Integer(description="Timestamp of when the access token will expire, in milliseconds")
})

user_token_pair = api.inherit("User token set", user_access_token, {
    "refreshToken": fields.String(description="Token presented to the server at any time to obtain a new access token."),
    "type": fields.String("Bearer", description="HTTP authorization token type")
})

flower_id = api.model("Flower ID", {  # WHY does this need to exist?!
    "flower_id": fields.Integer(description="Flower ID")
})

flower_dict_entry = api.model("Flowerdex entry", {
    "flower_id": fields.Integer(description="Flower ID"),
    "flower_latin_name": fields.Integer(description="Latin genus+species flower designation"),
    "flower_common_name": fields.String(description="Plain English flower name")
})

flower_shape = api.model("Flower shape", {
    "feature_id": fields.String(description="3-character flower shape identifier, prefixed with `fs`", example="fs5"),
    "feature_name": fields.String(description="Plain English description of the flower shape/feature", example="Tube with Spur"),
    "feature_description": fields.String(description="Alterate/longer description of feature", example="spiked tube"),
    "feature_pic_path": fields.String(description="File path under this server to image associated with the feature")
})

unmatched_flower = api.model("Unmatched flower", {
    "flower_name": fields.String(description="Flower name as reported by the user"),
    "count": fields.String(description="Count of times this flower occurs in the bee records database. Yes, this is an integer transmitted as a string.")
})

flower = api.model("Flower", {
    "flower_id": fields.Integer(description="Flowerdex ID"),
    "latin_name": fields.String(description="Latin genus+species flower designation"),
    "main_common_name": fields.String(description="Plain English flower name"),
    "common_name": fields.String(description="Alternate English name, what the flower is typically referred to as"),
    "colors": fields.String(description="Comma-separated list of the flower's colors", example="White,Purple"),
    "bloom_time": fields.String(description="Comma-separated list of month abbreviations for when the flower blooms. Often null.", example="Jun,Jul,Aug"),
    "shape": fields.String(description="Flower shape (see flower shape model for information)"),
    "img_src": fields.String(description="File path under this server to image associated with the flower. Usually null.")
})

###################
# RESPONSE MODELS #
###################

response_wrapper = api.model("Standard response wrapper", {
    "status": fields.String("success", description="Success status", enum=["success", "false"]),
    "message": fields.String(description="Information about operation performed"),
    "error": fields.Boolean(False, description="Success status")
})

bee_record_no_elevation_response = api.inherit("Bee record (w/o elevation) response", response_wrapper, {
    "data": fields.List(fields.Nested(bee_record_no_elevation))
})

bee_record_response = api.inherit("Bee record response", response_wrapper, {
    "data": fields.List(fields.Nested(bee_record))
})

bee_record_by_page_response = api.inherit("Bee record list (extended) response", response_wrapper, {
    "data": fields.List(fields.Nested(bee_record_extended))
})

bee_vis_record_response = api.inherit("Bee vis records response", response_wrapper, {
    "data": fields.List(fields.Nested(bee_vis_record))
})

beedex_response = api.inherit("Beedex entry response", response_wrapper, {
    "data": fields.List(fields.Nested(beedex_entry), description="Only ever contains one item.")
})

add_flower_response = api.inherit("Add flower response", response_wrapper, {
    "data": fields.List(fields.Nested(flower_id), description="Only ever contains one item.")
})

flower_dict_response = api.inherit("Flowerdex response", response_wrapper, {
    "data": fields.List(fields.Nested(flower_dict_entry))
})

flower_shape_response = api.inherit("Flower shape response", response_wrapper, {
    "data": fields.List(fields.Nested(flower_shape))
})

unmatched_flowers_response = api.inherit("Unmatched flowers response", response_wrapper, {
    "data": fields.List(fields.Nested(unmatched_flower))
})

flower_list_response = api.inherit("Flower list response", response_wrapper, {
    "data": fields.List(fields.Nested(flower))
})

media_upload_response = api.inherit("Media upload response", response_wrapper, {
    "imagePath": fields.String(description="File path on this server that the uploaded media was stored at")
})

news_response = api.inherit("News response", response_wrapper, {
    "data": fields.Raw(description="News object")
})

authorizations = {
    "user": {
        "type": "apiKey",
        "in": "header",
        "name": "Authorization"
    },
    "admin": {
        "type": "apiKey",
        "in": "header",
        "name": "Authorization"
    },
    "firebase": {
        "type": "apiKey",
        "in": "header",
        "name": "Authorization"
    }
}

###########
# PARSERS #
###########

bee_record_update_parser = reqparse.RequestParser()
bee_record_update_parser.add_argument("gender", type=str, required=False, help="Bee gender", choices=["male", "female", "male/female", "unknown"])
bee_record_update_parser.add_argument("fname", type=str, required=False, dest="flower_name", help="Flower name")
bee_record_update_parser.add_argument("fcolor", type=str, required=False, dest="flower_color", help="Flower color")
bee_record_update_parser.add_argument("beename", type=str, required=False, dest="bee_name", help="Bee name")
bee_record_update_parser.add_argument("beebehavior", type=str, required=False, dest="bee_behavior", help="Bee behavior")
bee_record_update_parser.add_argument("beedictid", type=int, required=False, dest="bee_dict_id", help="Bee dict ID")

bee_record_parser = reqparse.RequestParser()
bee_record_parser.add_argument("chead", type=str, required=True, dest="coloration_head", help="Head color")
bee_record_parser.add_argument("cabdomen", type=str, required=True, dest="coloration_abdomen", help="Abdomen color")
bee_record_parser.add_argument("cthorax", type=str, required=True, dest="coloration_thorax", help="Thorax color")
bee_record_parser.add_argument("gender", type=str, required=True, help="Gender", choices=["male", "female", "other", "unknown"])
bee_record_parser.add_argument("fname", type=str, required=True, dest="flower_name", help="Latin genus+species flower designation")
bee_record_parser.add_argument("cityname", type=str, required=True, dest="city_name"),
bee_record_parser.add_argument("fshape", type=str, required=True, dest="flower_shape", help="Flower color")
bee_record_parser.add_argument("fcolor", type=str, required=True, dest="flower_color", help="Flower color")
bee_record_parser.add_argument("beename", type=str, required=True, dest="bee_name", help="Latin genus+species bee designation"),
bee_record_parser.add_argument("loc", type=str, required=True, dest="loc_info", help="Comma-separate latitude-longitude coordinates")
bee_record_parser.add_argument("time", type=str, required=True, dest="time", help="%Y-%m-%dT%H:%M:%S.%fZ")
bee_record_parser.add_argument("recordpicpath", type=str, required=True, dest="record_pic_path", help="URL to image on this server")
bee_record_parser.add_argument("recordvideopath", type=str, required=False, dest="record_video_path", help="URL to video on this server")
bee_record_parser.add_argument("beedictid", type=str, required=False, dest="bee_dict_id")
bee_record_parser.add_argument("beebehavior", type=int, required=True, dest="bee_behavior", help="What the bee is collecting; 0: unknown; 1: nectar; 2: pollen")

new_flower_parser = reqparse.RequestParser()
new_flower_parser.add_argument("flowercommonname", required=True, type=str, dest="flower_common_name", help="Flower plain English name")
new_flower_parser.add_argument("flowershapeid", required=True, type=str, dest="flower_shape", help="Flower shape ID, usually something like `fs1`")
new_flower_parser.add_argument("flowercolorid", required=True, type=str, dest="flower_color", help="Flower color. Can be a comma-separated list.")
new_flower_parser.add_argument("flowerspecies", required=True, type=str, dest="flower_species", help="Latin flower species")
new_flower_parser.add_argument("flowergenus", required=True, type=str, dest="flower_genus", help="Latin flower genus")

update_flower_parser = reqparse.RequestParser()
update_flower_parser.add_argument("fcommon", required=False, type=str, dest="flower_common_name", help="Flower plain English name")
update_flower_parser.add_argument("fshape", required=False, type=str, dest="flower_shape", help="Flower shape ID, usually something like `fs1`")
update_flower_parser.add_argument("fcolor", required=False, type=str, dest="flower_color", help="Flower color. Can be a comma-separated list.")
update_flower_parser.add_argument("fspecies", required=False, type=str, dest="flower_species", help="Latin flower genus")
update_flower_parser.add_argument("fgenus", required=False, type=str, dest="flower_genus", help="Latin flower species")

video_parser = reqparse.RequestParser()
video_parser.add_argument("recordVideo", type=str, required=True, help="URL-safe base64-encoded image. Must have MIME type `video/*`")

image_parser = reqparse.RequestParser()
image_parser.add_argument("recordImage", type=str, required=True, help="URL-safe base64-encoded video. Must have MIME type `image/*`")

news_parser = reqparse.RequestParser()
news_parser.add_argument("json", type=dict, required=True, help="Any JSON (not a string)")
