from flask_restx import Namespace

from .endpoints import *

def setup_routes(ns: Namespace):
	ns.add_resource(RelativeFrequencies, "/relative-frequencies")
	ns.add_resource(SummaryStats, "/summary-stats")
