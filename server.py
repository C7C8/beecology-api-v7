import firebase_admin
from flask import Flask, Blueprint
from flask_cors import CORS
from flask_restplus import Api
from firebase_admin import credentials, auth as a

from utility import load_conf, setup_logging
from api_services import *

# Beecology API Server, Python edition!
# #####################################
#
# Configuration file format is specified in utility.py, you can copy/paste it into a json file ("conf.json" by default).
# This server will automatically log to WSGI's logging output at the level specified in the config file, as well as to
# a dedicated log file named in the configuration.
#
# Environment variables:
# BEE_API_CONF        Configuration file path ("conf.json" by default)

conf = load_conf()
setup_logging(conf["logging"])

app = Flask(__name__)
CORS(app)  # TODO: Holdover from node server, this may not be needed.
apiV7 = Blueprint('api', __name__)
api = Api(apiV7, version="1.0.0", title="Beecology data API", description="Processes requests to upload and download"
                                                                          " beecology data")
app.register_blueprint(apiV7)
ns = api.namespace("api_v7/api", "Beecology API version 7")
firebase_app = firebase_admin.initialize_app(credentials.Certificate(conf["auth"]["key-file"]),
                                             options=conf["auth"])

#########################################################
#                      API ROUTES                       #
#########################################################
ns.add_resource(Root, "/")
ns.add_resource(Root, "/isConnected")

# Bee data
ns.add_resource(Beedex, "/beedex/<int:id>")
ns.add_resource(Beedex, "/beedex")
ns.add_resource(BeeRecord, "/beerecord/<int:id>")
ns.add_resource(BeeRecordsList, "/beerecords/<int:page>")
ns.add_resource(BeeVisRecords, "/beevisrecords")
ns.add_resource(BeeUserRecords, "/beerecorduser")

# Flower data
ns.add_resource(Flowerdex, "/flowerdex")            # POST new flower
ns.add_resource(Flowerdex, "/flowerdex/<int:id>")   # GET or DELETE flower entry
ns.add_resource(FlowerList, "/flowerlist")           # Legacy support for flowerlist endpoint
ns.add_resource(FlowerShapes, "/flowershapes")
ns.add_resource(FlowerShapes, "/flowercolors")      # Not a typo, these seriously have the same handler...
ns.add_resource(UnmatchedFlowers, "/unmatched_flowers")

# Media upload
ns.add_resource(UploadImage, "/uploadImage64")
ns.add_resource(UploadVideo, "/uploadVideo")

# User management
ns.add_resource(RecordData, "/record")
ns.add_resource(Enroll, "/enroll")
ns.add_resource(Refresh, "/refresh")
ns.add_resource(Unenroll, "/unenroll")
#########################################################


if __name__ == '__main__':
	app.run()
