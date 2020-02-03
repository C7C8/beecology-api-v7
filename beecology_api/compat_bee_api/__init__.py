from .api import api
from .routes import setup_routes
import beecology_api.compat_bee_api.database

setup_routes(api)
__all__ = [api]
