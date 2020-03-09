from flask_restx import Namespace

main_api = Namespace("/", "Beecology data API")
reference_api = Namespace("/reference", "Beecology reference data, e.g. bee & flower species")
manage_api = Namespace("/management", "Administrator endpoints for managing the server")
