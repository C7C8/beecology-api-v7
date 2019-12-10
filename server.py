from flask import Flask, Blueprint
from flask_cors import CORS
from flask_restplus import Api, Resource

from utility import load_conf, setup_logging

# Beecology API Server, Python edition!
# =====================================
#
# Configuration file format is specified in utility.py, you can copy/paste it into a json file ("conf.json" by default).
# This server will automatically log to WSGI's logging output at the level specified in the config file, as well as to
# a dedicated log file named in the configuration.
#
# Environment variables:
# BEE_API_CONF        Configuration file path ("conf.json" by default)

conf = load_conf()
setup_logging(conf["logging"]["level"], conf["logging"]["file"])

app = Flask(__name__)
CORS(app)  # TODO: Holdover from node server, this may not be needed.
apiV7 = Blueprint('api', __name__)
api = Api(apiV7, version="1.0.0", title="Beecology data API", description="Processes requests to upload and download"
                                                                          " beecology data")
app.register_blueprint(apiV7)
ns = api.namespace("api_v7/api", "Beecology API version 7")


@ns.route("/")
class Root(Resource):
	def get(self):
		"""Return a simple 'yes, the app is working'-style message"""
		return "Welcome! The api is working!"


if __name__ == '__main__':
	app.run()
