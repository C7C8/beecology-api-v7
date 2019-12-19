import json
import os
import sys
import logging.config
from typing import Dict

from api_services import Config

__default_conf = {
	"storage": {
		"imageUploadPath": "images",
		"cache": "/tmp"
	},
	"database": {
		"pool_size": 16,
		"connection": {
			"host": "localhost",
			"dbname": "beecologydb",
			"user": "root",
			"password": "",
			"port": 5432
		}
	},
	"logging": {
		"version": 1,
		"formatters": {
			"default": {
				"format": "[%(asctime)s] %(levelname)s in %(module)s: %(message)s",
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
	# Config file is given by environment variable BEE_API_CONF, or conf.json if variable not provided.
	conf = __default_conf
	conf_file_name = os.environ["BEE_API_CONF"] if "BEE_API_CONF" in os.environ else "conf.json"
	try:
		with open(conf_file_name, "r") as conf_file:
			conf = json.load(conf_file)
	except IOError:
		print("Failed to load config file \"{}\" falling back to local default. THIS IS ALMOST GUARANTEED TO FAIL!"
		      .format(conf_file_name), file=sys.stderr)
	Config.config = conf
	return conf


def setup_logging(config=None):
	# Set up logging for Flask
	logging.config.dictConfig(__default_conf["logging"] if config is None else config)
