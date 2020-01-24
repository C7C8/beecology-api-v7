import json
import os
import sys
import logging.config
from typing import Dict

import yaml

from api_services import Config

__default_conf = {
	"auth": {
		"keyfile": "firebase.json",
		"token-lifetime": 3600
	},
	"admin-code": "SECRET_CODE",
	"storage": {
		"imageUploadPath": "images",
		"imageBasePath": "images",
		"news-path": "/tmp",
		"cache": "/tmp/beecology-cache"
	},
	"database": {
		"pool_size": 16,
		"connection": "postgresql+psycopg2://root@localhost:5432/beecologydb"
	},
	"logging": {
		"version": 1,
		"formatters": {
			"default": {
				"format": "[%(asctime)s] %(levelname)s in %(module): %(message)s",
			}
		},
		"handlers": {
			"wsgi": {
				"class": "logging.StreamHandler",
				"stream": "ext://flask.logging.wsgi_errors_stream",
				"formatter": "default"
			},
			"file": {
				"class": "logging.FileHandler",
				"filename": "log.txt",
				"formatter": "default"
			}
		},
		"root": {
			"level": "INFO",
			"handlers": ["wsgi", "file"]
		}
	}
}


def load_conf() -> Dict:
	# Load configuration file, fall back to default config if not available.
	# Config file is given by environment variable BEE_API_CONF, or conf.yml if variable not provided.
	conf = __default_conf
	conf_file_name = os.environ["BEE_API_CONF"] if "BEE_API_CONF" in os.environ else "conf.yml"

	# Use YAML loader or JSON loader depending on file extension
	load = json.load if ".json" in conf_file_name else yaml.safe_load

	try:
		with open(conf_file_name, "r") as conf_file:
			conf = load(conf_file)
	except IOError:
		print("Failed to load config file \"{}\" falling back to local default. THIS IS ALMOST GUARANTEED TO FAIL!"
		      .format(conf_file_name), file=sys.stderr)
	Config.config = conf
	return conf


def setup_logging(config=None):
	# Set up logging for Flask
	logging.config.dictConfig(__default_conf["logging"] if config is None else config)
