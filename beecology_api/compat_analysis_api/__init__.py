from .api import api
from .routes import setup_routes

setup_routes(api)
__all__ = [api]
