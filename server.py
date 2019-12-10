from flask import Flask

from utility import load_conf, setup_logging

"""
Beecology API Server, Python edition!
=====================================

Configuration file format is specified in utility.py, you can copy/paste it into a json file ("conf.json" by default).
This server will automatically log to WSGI's logging output at the level specified in the config file, as well as to
a dedicated log file named in the configuration.

Environment variables:
BEE_API_CONF        Configuration file path ("conf.json" by default)
"""

conf = load_conf()
setup_logging(conf["logging"]["level"], conf["logging"]["file"])

app = Flask(__name__)


@app.route('/')
def hello_world():
	return 'Hello World!'


if __name__ == '__main__':
	app.run()
