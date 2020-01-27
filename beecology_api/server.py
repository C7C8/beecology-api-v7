import firebase_admin
from flask import Flask, Blueprint
from flask_cors import CORS
from flask_restplus import Api
from firebase_admin import credentials
import logging.config

import beecology_api.api.endpoints as endpoints
from beecology_api.api.api import api
import beecology_api.config as config

# Beecology API Server, Python edition!
# #####################################
#
# Configuration file format is specified in config.py, you can copy/paste it into a JSON file.
# or you can use YML to configure the server, following the same layout.
#
# This server will automatically log to WSGI's logging output at the level specified in the config file, as well as to
# a dedicated log file named in the configuration.
#
# Environment variables:
# BEE_API_CONF        Configuration file path ("conf.yml" by default)

app = Flask(__name__)
ns: Api = None


def init_api():
	global ns
	config.load_config()
	logging.config.dictConfig(config.config["logging"])

	CORS(app)  # TODO: Holdover from node server, this may not be needed.
	blueprint = Blueprint("api", __name__)
	api.init_app(blueprint)
	app.register_blueprint(blueprint)
	ns = api.namespace("/", "Beecology API version 7")
	firebase_app = firebase_admin.initialize_app(credentials.Certificate(config.config["auth"]["key-file"]),
	                                             options=config.config["auth"])
	setup_routes()


def setup_routes():
	#########################################################
	#                      API ROUTES                       #
	#########################################################
	ns.add_resource(endpoints.IsConnected, "/isConnected")

	# Bee data
	ns.add_resource(endpoints.Beedex, "/beedex/<int:id>")
	ns.add_resource(endpoints.Beedex, "/beedex")
	ns.add_resource(endpoints.BeeRecord, "/beerecord/<int:id>")
	ns.add_resource(endpoints.BeeRecordsList, "/beerecords/<int:page>")
	ns.add_resource(endpoints.BeeVisRecords, "/beevisrecords")
	ns.add_resource(endpoints.BeeUserRecords, "/beerecorduser")
	ns.add_resource(endpoints.RecordData, "/record")
	ns.add_resource(endpoints.NoElevationData, "/noelevationrecords")

	# Flower data -- don't look at me like that! I didn't write the API interface spec!
	ns.add_resource(endpoints.AddFlower, "/addflower")
	ns.add_resource(endpoints.GetFlower, "/flowerdex/<int:id>")
	ns.add_resource(endpoints.DeleteFlower, "/deleteflower/<int:id>")
	ns.add_resource(endpoints.FlowerList, "/flowerlist")                # Legacy support for flowerlist endpoint
	ns.add_resource(endpoints.FlowerShapes, "/flowershapes")
	ns.add_resource(endpoints.FlowerShapes, "/flowercolors")            # Not a typo, these have the same handler...
	ns.add_resource(endpoints.UnmatchedFlowers, "/unmatched_flowers")

	# Media upload
	ns.add_resource(endpoints.UploadImage, "/uploadImage64")
	ns.add_resource(endpoints.UploadVideo, "/uploadVideo")

	# Login/refresh/logout
	ns.add_resource(endpoints.Enroll, "/enroll")
	ns.add_resource(endpoints.Refresh, "/refresh")
	ns.add_resource(endpoints.Unenroll, "/unenroll")

	# News
	ns.add_resource(endpoints.BioCSNews, "/update_biocsnews")
	ns.add_resource(endpoints.BioCSNews, "/biocsnews")
	ns.add_resource(endpoints.News, "/update_news")
	ns.add_resource(endpoints.News, "/news")

	# Admin
	ns.add_resource(endpoints.VerifyAdmin, "/verifyAdmin")
	#########################################################


if __name__ == '__main__' or __name__ == "beecology_api.server":
	init_api()
	app.run()
