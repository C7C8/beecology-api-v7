import logging.config

import firebase_admin
from firebase_admin import credentials
from flask import Flask, Blueprint
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_restx import Api

import beecology_api.config as config
from beecology_api import compat_bee_api, compat_analysis_api, beecology_api, analysis_api
from beecology_api.compat_bee_api.models import authorizations as bee_authorizations
from beecology_api.db import init_database as main_db_init

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
jwt = JWTManager(app)


def init_api():
	config.load_config()
	logging.config.dictConfig(config.config["logging"])
	app.config["JWT_SECRET_KEY"] = config.config["auth"]["jwt-key"]
	main_db_init()

	CORS(app)
	blueprint = Blueprint("api", __name__)
	firebase_app = firebase_admin.initialize_app(credentials.Certificate(config.config["auth"]["key-file"]),
	                                             options=config.config["auth"])

	# Set up API and register namespaces
	api = Api(blueprint,
	          title="Beecology API",
	          description="The Beecology API, for uploading/downloading Beecology data or performing data analyses",
	          contact_email="beecologyproject@wpi.edu",
	          version="2.0.0",
	          default_mediatype="application/json",
	          authorizations=bee_authorizations,
	          validate=True)
	api.add_namespace(beecology_api.main_api)
	api.add_namespace(beecology_api.reference_api, "/reference")
	api.add_namespace(beecology_api.manage_api, "/management")
	api.add_namespace(analysis_api.api, "/analysis")
	# api.add_namespace(compat_analysis_api.api, "/compat/analysis")
	# api.add_namespace(compat_bee_api.api, "/compat")

	app.register_blueprint(blueprint)
	jwt._set_error_handler_callbacks(api)  # hack: plz stop returning 500 Server Error


init_api()
