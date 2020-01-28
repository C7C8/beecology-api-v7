from .api import *
from .routes import setup_routes

setup_routes(api)

__all__ = [api]
