from logging import getLogger

import sqlalchemy.pool
from sqlalchemy import create_engine, Table, Column, Integer, String, Text, SmallInteger, ForeignKey, DateTime, \
	BigInteger
from sqlalchemy.engine import Engine
from sqlalchemy.exc import NoSuchTableError

from beecology_api import config

log = getLogger()

engine: Engine = None
beedict: sqlalchemy.Table = None
beerecord: sqlalchemy.Table = None
flower: sqlalchemy.Table = None
flowerdict: sqlalchemy.Table = None
features: sqlalchemy.Table = None
auth: sqlalchemy.Table = None
admin: sqlalchemy.Table = None


def get_engine() -> Engine:
	"""Get a SQLAlchemy engine object"""
	global engine, beedict, beerecord, flower, flowerdict, features, auth, admin
	if engine is None:
		log.debug("Starting SQLAlchemy engine for legacy database")
		dbconfig = config.config["legacy-database"]

		try:
			# Exact dialect+driver is specified by the config file
			cxn_str = dbconfig["connection"]
			engine = create_engine(cxn_str, pool_size=dbconfig["pool_size"]) if "sqlite" not in cxn_str else create_engine(cxn_str)
		except Exception as e:
			log.critical("Failed to connect to database: {}".format(e))
			raise e

		try:
			metadata = sqlalchemy.MetaData()
			beedict = sqlalchemy.Table("beedict", metadata, autoload=True, autoload_with=engine)
			beerecord = sqlalchemy.Table("beerecord", metadata, autoload=True, autoload_with=engine)
			flower = sqlalchemy.Table("flower", metadata, autoload=True, autoload_with=engine)
			flowerdict = sqlalchemy.Table("flowerdict", metadata, autoload=True, autoload_with=engine)
			features = sqlalchemy.Table("feature", metadata, autoload=True, autoload_with=engine)
			auth = sqlalchemy.Table("authtable", metadata, autoload=True, autoload_with=engine)
			admin = sqlalchemy.Table("admintable", metadata, autoload=True, autoload_with=engine)
		except NoSuchTableError:
			log.warning("Failed to find table ({}), assuming we need to initialize the database")
			log.warning("Creating tables from scratch may result in some unit tests failing due to missing data")
			__create_schema(engine)

	return engine


def __create_schema(engine):
	global beedict, beerecord, flower, flowerdict, features, auth, admin
	metadata = sqlalchemy.MetaData()
	beedict = Table("beedict", metadata,
	                Column("bee_id", SmallInteger(), primary_key=True),
	                Column("bee_name", String(128)),
	                Column("common_name", String(256)),
	                Column("description", Text()),
	                Column("active_months", String(128)),
	                Column("confused", Text()),
	                Column("bee_pic_path", String(1024)),
	                Column("abdomen_list", String(256)),
	                Column("thorax_list", String(256)),
	                Column("head_list", String(256)))

	beerecord = Table("beerecord", metadata,
	                  Column("beerecord_id", Integer(), primary_key=True),
	                  Column("bee_dict_id", SmallInteger(), ForeignKey("beedict.bee_id"), nullable=True),
	                  Column("bee_name", String(128)),
	                  Column("coloration_abdomen", String(4)),
	                  Column("coloration_thorax", String(4)),
	                  Column("coloration_head", String(4)),
	                  Column("flower_shape", String(128)),
	                  Column("flower_color", String(16)),
	                  Column("time", DateTime()),
	                  Column("loc_info", String(32)),
	                  Column("user_id", String(64), index=True),
	                  Column("record_pic_path", String(1024)),
	                  Column("record_video_path", String(1024)),
	                  Column("flower_name", String(256)),
	                  Column("city_name", String(256)),
	                  Column("gender", String(16)),
	                  Column("bee_behavior", String(16)),
	                  Column("app_version", String(16)),
	                  Column("elevation", String(8)))

	flower = Table("flower", metadata,
	               Column("flower_id", Integer(), primary_key=True),
	               Column("flower_common_name", String(128)),
	               Column("flower_genus", String(64)),
	               Column("flower_species", String(64)),
	               Column("flower_color", String(16)),
	               Column("flower_shape", String(8)))

	flowerdict = Table("flowerdict", metadata,
	                   Column("flower_id", Integer(), primary_key=True),
	                   Column("latin_name", String(128), index=True),
	                   Column("common_name", String(128)),
	                   Column("main_common_name", String(128)),
	                   Column("main_color", String(16)),
	                   Column("colors", Text()),
	                   Column("bloom_time", Text()),
	                   Column("shape", String(32)))

	features = Table("feature", metadata,
	                 Column("feature_id", String(8), primary_key=True),
	                 Column("feature_name", String(32)),
	                 Column("feature_description", Text()),
	                 Column("feature_pic_path", String(1024)))

	auth = Table("authtable", metadata,
	             Column("user_id", String(512), primary_key=True),
	             Column("access_token", String(1024), index=True),
	             Column("refresh_token", String(1024), index=True),
	             Column("token_expiry", BigInteger()))

	admin = Table("admintable", metadata,
	              Column("user_id", String(512), ForeignKey("authtable.user_id", ondelete="cascade"), index=True))

	metadata.create_all(engine)
