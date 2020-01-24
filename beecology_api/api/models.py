from flask_restplus import reqparse, fields

from beecology_api.api.api import api

###############
# DATA MODELS #
###############

bee_record = api.model("Bee record", {
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
    "record_pic_path": fields.String(description="The file the image associated with this record may be found at under this server"),
    "record_video_path": fields.String(description="Unused. Currently left blank."),
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

###################
# RESPONSE MODELS #
###################

response_model = api.model("Standard response wrapper", {
    "success": fields.String(description="Success status", enum=["success", "false"]),
    "message": fields.String(description="Information about operation performed"),
    "error": fields.Boolean(description="Success status")
})


bee_record_response = api.inherit("Bee record response", response_model, {
    "data": fields.Nested(bee_record)
})

bee_record_by_page_response = api.inherit("Bee record page response", response_model, {
    "data": fields.List(fields.Nested(bee_record_extended))
})

bee_vis_record_response = api.inherit("Bee vis records response", response_model, {
    "data": fields.List(fields.Nested(bee_vis_record))
})


###########
# PARSERS #
###########

bee_record_update = reqparse.RequestParser()
bee_record_update.add_argument("gender", type=str, required=False, help="Bee gender", choices=["male", "female", "male/female", "unknown"])
bee_record_update.add_argument("fname", type=str, required=False, dest="flower_name", help="Flower name")
bee_record_update.add_argument("fcolor", type=str, required=False, dest="flower_color", help="Flower color")
bee_record_update.add_argument("beename", type=str, required=False, dest="bee_name", help="Bee name")
bee_record_update.add_argument("beebehavior", type=str, required=False, dest="bee_behavior", help="Bee behavior")
bee_record_update.add_argument("beedictid", type=int, required=False, dest="bee_dict_id", help="Bee dict ID")
