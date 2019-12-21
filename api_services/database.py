from logging import getLogger

import psycopg2
import sqlalchemy.pool
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

from .config import Config

log = getLogger()


class Database:
	"""Service that wraps PostgreSQL connection pooling. __enter__ sets up the pool if needed and gets an engine from it;
	the engine is saved locally while pool is a static, so we can use with .. as .. : syntax to automatically handle
	getting and returning connections"""

	pool: Engine = None
	beedict: sqlalchemy.Table = None
	beerecord: sqlalchemy.Table = None
	flower: sqlalchemy.Table = None
	flowerdict: sqlalchemy.Table = None
	features: sqlalchemy.Table = None
	auth: sqlalchemy.Table = None

	@staticmethod
	def get_connection():
		dbconfig = Config.config["database"]
		log.debug("Establishing new connection to database {user}@{host}:{port}/{dbname}".format(**dbconfig["connection"]))
		return psycopg2.connect(**dbconfig["connection"])

	def __enter__(self) -> Engine:
		"""Get a connection object"""
		if Database.pool is None:
			log.debug("Starting SQLAlchemy engine")
			dbconfig = Config.config["database"]

			try:
				Database.pool = create_engine("postgresql+psycopg2://", creator=Database.get_connection,
											  pool_size=dbconfig["pool_size"])
			except Exception as e:
				log.critical("Failed to connect to database: {}".format(e))
				raise e

			metadata = sqlalchemy.MetaData()
			Database.beedict = sqlalchemy.Table("beedict", metadata, autoload=True, autoload_with=Database.pool)
			Database.beerecord = sqlalchemy.Table("beerecord", metadata, autoload=True, autoload_with=Database.pool)
			Database.flower = sqlalchemy.Table("flower", metadata, autoload=True, autoload_with=Database.pool)
			Database.flowerdict = sqlalchemy.Table("flowerdict", metadata, autoload=True, autoload_with=Database.pool)
			Database.features = sqlalchemy.Table("feature", metadata, autoload=True, autoload_with=Database.pool)
			Database.auth = sqlalchemy.Table("authtable", metadata, autoload=True, autoload_with=Database.pool)

		return self.pool

	def __exit__(self, exc_type, exc_val, exc_tb):
		"""Return the connection back to the pool"""
		# TODO Delete
		if exc_type is not None:
			log.critical("Error re-pooling connection: {}, {}, {}".format(exc_type, exc_val, exc_tb))
