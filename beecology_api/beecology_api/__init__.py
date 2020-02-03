from .api import main_api, reference_api, manage_api
from .routes import setup_main_routes, setup_reference_routes, setup_admin_routes
import beecology_api.beecology_api.db

setup_main_routes(main_api)
setup_reference_routes(reference_api)
setup_admin_routes(manage_api)
__all__ = [main_api, reference_api]
