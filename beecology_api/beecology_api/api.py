from flask_restx import Namespace

main_api = Namespace("/prototype", "Prototype beecology data API")
reference_api = Namespace("/prototype/reference", "Beecology reference data, e.g. bee & flower species")
manage_api = Namespace("/prototype/management", "Administrator endpoints for managing the server")
