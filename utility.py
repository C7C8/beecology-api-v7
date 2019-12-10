import json
import os
import sys
from logging.config import dictConfig
from typing import Dict


def load_conf() -> Dict:
	# Load configuration file, fall back to default config if not available.
	# Config file is given by environment variable BEE_API_CONF, or conf.json if variable not provided.
	conf = {
		"imageUploadPath": "../../../../images",
		"logging": {
			"file": "log.txt",
			"level": "WARNING",
		},
		"database": {
			"host": "localhost",
			"database": "beecologydb",
			"user": "root",
			"password": ""
		}
	}
	conf_file_name = os.environ["BEE_API_CONF"] if "BEE_API_CONF" in os.environ else "conf.json"
	try:
		with open(conf_file_name, "r") as conf_file:
			conf = json.load(conf_file)
	except IOError:
		print("Failed to load config file \"{}\" falling back to local default. THIS IS ALMOST GUARANTEED TO FAIL!"
		      .format(conf_file_name), file=sys.stderr)
	return conf


def setup_logging(level: str, filename: str):
	# Set up logging for Flask
	dictConfig({
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
				"filename": filename,
				"formatter": "default"
			}
		},
		"root": {
			"level": level,
			"handlers": ["wsgi", "file"]
		}
	})
