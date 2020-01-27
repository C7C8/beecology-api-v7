from flask_restplus import reqparse, fields

from beecology_api.api.api import api

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
    "abdomen_list": fields.String(description="List of abdomens associated with this bee. Usually null.", example="{\"a3\", \"a13\"}"),
    "thorax list": fields.String(description="List of thoraxes associated with this bee. Usually null.", example="{\"t1\", \"t1\"}"),
    "head_list": fields.String(description="List of heads associated with this bee. Usually null.", example="{\"h2\", \"h3\"}")
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
    "data": fields.Nested(bee_record_no_elevation)
})

bee_record_response = api.inherit("Bee record response", response_wrapper, {
    "data": fields.Nested(bee_record)
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
