from sqlalchemy import create_engine

from beecology_api import config

dbconfig = config.config["database"]
cxn_str = dbconfig["connection"]
db = create_engine(cxn_str, pool_size=dbconfig["pool_size"]) if "sqlite" not in cxn_str else create_engine(cxn_str)

