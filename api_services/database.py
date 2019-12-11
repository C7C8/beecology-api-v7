from logging import getLogger

from psycopg2.pool import ThreadedConnectionPool

from .config import Config

log = getLogger()

class DatabaseService:
	"""Service that wraps PostgreSQL connection pooling"""
	pool: ThreadedConnectionPool = None

	def __enter__(self):
		"""Get a connection object"""
		if DatabaseService.pool is None:
			log.debug("Instantiating thread pool")
			dbconfig = Config.config["database"]
			log.info("Connecting to database {user}@{host}:{port}/{dbname}".format(**dbconfig["connection"]))

			try:
				DatabaseService.pool = ThreadedConnectionPool(dbconfig["pool_min"], dbconfig["pool_max"], **dbconfig["connection"])
			except Exception as e:
				log.critical("Failed to connect to database: {}".format(e))
				raise e

		self.conn = DatabaseService.pool.getconn()
		return self.conn.cursor()

	def __exit__(self, exc_type, exc_val, exc_tb):
		"""Return the connection back to the pool"""
		if exc_type is not None:
			log.warning("Error re-pooling connection: {}, {}, {}".format(exc_type, exc_val, exc_tb))
			return
		DatabaseService.pool.putconn(self.conn)
