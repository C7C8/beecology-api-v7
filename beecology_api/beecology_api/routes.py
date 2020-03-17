from flask_restx import Namespace

from .endpoints import *


#########################################################
#                      API ROUTES                       #
#########################################################

def setup_main_routes(main: Namespace):
	main.add_resource(Media, "/media/<uuid:id>", methods=["DELETE", "PUT", "GET"])
	main.add_resource(Media, "/media", methods=["POST"])
	main.add_resource(Token, "/token")
	main.add_resource(Refresh, "/refresh")
	main.add_resource(Record, "/record", methods=["POST"])
	main.add_resource(Record, "/record/<uuid:id>", methods=["DELETE", "PUT", "GET"])
	main.add_resource(Records, "/records")
	main.add_resource(CSVRecords, "/csv")
	main.add_resource(News, "/news", methods=["GET"])
	main.add_resource(News, "/news/<uuid:id>", methods=["PUT", "POST", "DELETE"])


def setup_reference_routes(ref: Namespace):
	ref.add_resource(Bee, "/bee", methods=["POST"])
	ref.add_resource(Bee, "/bee/<uuid:id>", methods=["DELETE", "PUT", "GET"])
	ref.add_resource(Bees, "/bees")
	ref.add_resource(Flower, "/flower", methods=["POST"])
	ref.add_resource(Flower, "/flower/<uuid:id>", methods=["DELETE", "PUT", "GET"])
	ref.add_resource(Flowers, "/flowers")
	ref.add_resource(FlowerDistinctValues, "/flowers/distinct-values")


def setup_admin_routes(manage: Namespace):
	manage.add_resource(User, "/user/<string:id>")
	manage.add_resource(Users, "/users")
	# manage.add_resource(Admin, "/admin/<string:id>")
	# manage.add_resource(ChangeAdmin, "/admin")
