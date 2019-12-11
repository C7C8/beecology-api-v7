from psycopg2.pool import ThreadedConnectionPool

from .config import Config

class DatabaseService:
	"""Service that wraps PostgreSQL connection pooling"""
	pool: ThreadedConnectionPool = None

	def __enter__(self):
		"""Get a connection object"""
		if DatabaseService.pool is None:
			dbconfig = Config.config["database"]
			DatabaseService.pool = ThreadedConnectionPool(dbconfig["pool_min"], dbconfig["pool_max"], **dbconfig["connection"])

		self.conn = DatabaseService.pool.getconn()
		return self.conn

	def __exit__(self, exc_type, exc_val, exc_tb):
		"""Return the connection back to the pool"""
		DatabaseService.pool.putconn(self.conn)
