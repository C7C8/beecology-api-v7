from flask_restx import Namespace

from .endpoints import *

#########################################################
#                      API ROUTES                       #
#########################################################

def setup_main_routes(main: Namespace):
	main.add_resource(Image, "/image/<uuid:id>", defaults={"id": None})
	main.add_resource(Video, "/video/<uuid:id>", defaults={"id": None})
	main.add_resource(Token, "/token")
	main.add_resource(Record, "/record/<uuid:id>")
	main.add_resource(AddRecord, "/record")


def setup_reference_routes(ref: Namespace):
	ref.add_resource(Bee, "/bee-species/<uuid:id>", defaults={"id": None})
	ref.add_resource(Flower, "/flower-species<uuid:id>", defaults={"id": None})

def setup_admin_routes(manage: Namespace):
	manage.add_resource(User, "/user/<string:id>")
	manage.add_resource(Admin, "/admin/<string:id>")
