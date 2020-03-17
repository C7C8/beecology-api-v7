from flask_restx import reqparse, inputs, fields

from beecology_api.db import genders, beehaviors

bee_record_filter_parser = reqparse.RequestParser()
bee_record_filter_parser.add_argument("user-id", type=str, help="User ID", required=False, dest="user_id")
bee_record_filter_parser.add_argument("species", type=str, help="Species UUID", required=False, dest="bee_species_id", action="split")
bee_record_filter_parser.add_argument("flower-species", type=str, help="Flower species UUID", required=False, dest="flower_species_id", action="split"),
bee_record_filter_parser.add_argument("head", type=str, help="Head type", required=False, dest="head_coloration", action="split")
bee_record_filter_parser.add_argument("abdomen", type=str, help="Abdomen type", required=False, dest="abdomen_coloration", action="split")
bee_record_filter_parser.add_argument("thorax", type=str, help="Thorax type", required=False, dest="thorax_coloration", action="split")
bee_record_filter_parser.add_argument("time-start", type=inputs.datetime, help="Time that records must fall at or after", required=False)
bee_record_filter_parser.add_argument("time-end", type=inputs.datetime, help="Time that records must fall at or before", required=False)
bee_record_filter_parser.add_argument("city", type=str, help="City that records must be located in", required=False, dest="closest_city")
bee_record_filter_parser.add_argument("gender", type=str, help="Bee gender", required=False, action="split")
bee_record_filter_parser.add_argument("behavior", type=str, help="Bee beehavior", required=False, action="split")
bee_record_filter_parser.add_argument("max-elevation", type=float, help="Elevation that records must be at or below", required=False)
bee_record_filter_parser.add_argument("min-elevation", type=float, help="Elevation that records must be at or above", required=False)
bee_record_filter_parser.add_argument("bounding-box", type=str, help="Bounding box that records must fall in, in format minLat,minLong,maxLat,maxLong", required=False)
