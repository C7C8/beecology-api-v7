from flask_restplus import Namespace

from .endpoints import *

def setup_routes(ns: Namespace):
	ns.add_resource(Index, "/")
	ns.add_resource(Index, "/index")
	ns.add_resource(Error, "/error")
	ns.add_resource(TestError, "/test_error")
