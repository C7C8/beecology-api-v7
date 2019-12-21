from logging import getLogger

import psycopg2
import sqlalchemy.pool
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

from .config import Config

log = getLogger()

engine: Engine = None
beedict: sqlalchemy.Table = None
beerecord: sqlalchemy.Table = None
flower: sqlalchemy.Table = None
flowerdict: sqlalchemy.Table = None
features: sqlalchemy.Table = None
auth: sqlalchemy.Table = None


def __get_postgres_connection():
	dbconfig = Config.config["database"]
	log.debug("Establishing new connection to database {user}@{host}:{port}/{dbname}".format(**dbconfig["connection"]))
	return psycopg2.connect(**dbconfig["connection"])

def get_engine() -> Engine:
	"""Get a SQLAlchemy engine object"""
	global engine, beedict, beerecord, flower, flowerdict, features, auth
	if engine is None:
		log.debug("Starting SQLAlchemy engine")
		dbconfig = Config.config["database"]

		try:
			engine = create_engine("postgresql+psycopg2://", creator=__get_postgres_connection,
			                              pool_size=dbconfig["pool_size"])
		except Exception as e:
			log.critical("Failed to connect to database: {}".format(e))
			raise e

		metadata = sqlalchemy.MetaData()
		beedict = sqlalchemy.Table("beedict", metadata, autoload=True, autoload_with=engine)
		beerecord = sqlalchemy.Table("beerecord", metadata, autoload=True, autoload_with=engine)
		flower = sqlalchemy.Table("flower", metadata, autoload=True, autoload_with=engine)
		flowerdict = sqlalchemy.Table("flowerdict", metadata, autoload=True, autoload_with=engine)
		features = sqlalchemy.Table("feature", metadata, autoload=True, autoload_with=engine)
		auth = sqlalchemy.Table("authtable", metadata, autoload=True, autoload_with=engine)

	return engine
