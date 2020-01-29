from flask_restplus import Namespace

from .endpoints import *

def setup_routes(ns: Namespace):
	ns.add_resource(Index, "/")
	ns.add_resource(Index, "/index")
	ns.add_resource(Error, "/error")
	ns.add_resource(TestError, "/test_error")

	ns.add_resource(RunModel, "/runModel")
	ns.add_resource(CrossTabulation, "/cross-tabulation")
	ns.add_resource(DecisionTree, "/decision-tree")
	ns.add_resource(KMeans, "/k-means")
	ns.add_resource(LinearRegression, "/linear-regression")
	ns.add_resource(RelativePercent, "/relative-percent")
	ns.add_resource(Trend, "/trend")
	ns.add_resource(NonlinearRegression, "/nonlinear-regression")
