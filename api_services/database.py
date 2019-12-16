from logging import getLogger

import psycopg2
import sqlalchemy.pool
from sqlalchemy import create_engine

from .config import Config

log = getLogger()

class DatabaseService:
	"""Service that wraps PostgreSQL connection pooling"""
	engine: sqlalchemy.pool.Pool = None

	@staticmethod
	def get_connection():
		dbconfig = Config.config["database"]
		log.info("Connecting to database {user}@{host}:{port}/{dbname}".format(**dbconfig["connection"]))
		return psycopg2.connect(**dbconfig["connection"])

	def __enter__(self):
		"""Get a connection object"""
		if DatabaseService.engine is None:
			log.debug("Starting SQLAlchemy engine")
			dbconfig = Config.config["database"]

			try:
				DatabaseService.engine = create_engine("postgresql+psycopg2://", creator=DatabaseService.get_connection,
				                                       pool_size=dbconfig["pool_size"])
			except Exception as e:
				log.critical("Failed to connect to database: {}".format(e))
				raise e

		self.conn = DatabaseService.get_connection()
		return self.conn.cursor()

	def __exit__(self, exc_type, exc_val, exc_tb):
		"""Return the connection back to the pool"""
		if exc_type is not None:
			log.warning("Error re-pooling connection: {}, {}, {}".format(exc_type, exc_val, exc_tb))
			return
		self.conn.close()
