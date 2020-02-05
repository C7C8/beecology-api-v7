from logging import getLogger

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from beecology_api import config
from .models import *


Session = None

def init_database():
	global Session
	getLogger().debug("Starting SQL engine for main beecology database")
	db_config = config.config["database"]
	cxn_str = db_config["connection"]
	engine = create_engine(cxn_str, pool_size=db_config["pool_size"]) if "sqlite" not in cxn_str else create_engine(cxn_str)
	BaseTable.metadata.create_all(engine)
	Session = sessionmaker(bind=engine)
