from datetime import datetime

from geoalchemy2 import Geometry
from sqlalchemy import Column, String, DateTime, Enum, Float, ForeignKey, Boolean, Text, JSON
from sqlalchemy.dialects import postgresql
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from beecology_api import config
import beecology_api.beecology_api.db as db


use_postgres = "postgres" in config.config["database"]["connection"]
id_type = postgresql.UUID(as_uuid=True) if use_postgres else String
Base = declarative_base()


class User(Base):
	__tablename__       = "user"
	id                  = Column(String, primary_key=True, index=True)
	admin               = Column(Boolean, default=False)
	locked              = Column(Boolean, default=False)
	registered          = Column(DateTime, default=datetime.now())
	last_login          = Column(DateTime, default=datetime.now())
	records             = relationship("BeeRecord")
	images              = relationship("Image")
	videos              = relationship("Video")
	news                = relationship("News")


class BeeRecord(Base):
	__tablename__       = "bee_record"
	id                  = Column(id_type, primary_key=True, index=True)
	user                = Column(String, ForeignKey("user.id", ondelete="SET NULL"), index=True)
	bee_species_id      = Column(id_type, ForeignKey("bee_species.id"), index=True)
	flower_species_id   = Column(id_type, ForeignKey("flower_species.id"), index=True)
	images              = relationship("Image", backref="bee_record")
	videos              = relationship("Video", backref="bee_record")
	name                = Column(String)
	abdomen             = Column(String)
	thorax              = Column(String)
	time                = Column(DateTime)
	loc_info            = Column(Geometry(geometry_type="POINT") if use_postgres else String)
	city                = Column(String)
	gender              = Column(Enum("male", "female", "either", "unknown", name="bee_gender"))
	behavior            = Column(Enum("pollen", "nectar", "unknown", name="bee_behavior"))
	elevation           = Column(Float)


class BeeSpecies(Base):
	__tablename__       = "bee_species"
	id                  = Column(id_type, primary_key=True, index=True)
	genus               = Column(String)
	species             = Column(String)
	common_name         = Column(String)
	description         = Column(Text)
	active_start        = Column(Enum("January", "February", "March", "April", "May", "June", "July", "August", "September",
	                                  "October", "November", "December", name="months"))
	active_end          = Column(Enum(name="months"))
	confused_with       = Column(String)
	image               = Column(String)
	records             = relationship("BeeRecord", backref="bee_species")


class FlowerSpecies(Base):
	__tablename__       = "flower_species"
	id                  = Column(id_type, primary_key=True, index=True)
	genus               = Column(String)
	species             = Column(String)
	common_name         = Column(String)
	alt_name            = Column(String)
	main_color          = Column(String)
	colors              = Column(String)
	bloom_start         = Column(Enum(name="months"))
	bloom_end           = Column(Enum(name="months"))
	shape               = Column(String)
	image               = Column(String)
	records             = relationship("BeeRecord", backref="flower_species")


class Image(Base):
	__tablename__       = "image"
	id                  = Column(id_type, primary_key=True)
	bee_record_id       = Column(id_type, ForeignKey("bee_record.id"), index=True)
	user_id             = Column(String, ForeignKey("user.id"))
	path                = Column(String)


class Video(Base):
	__tablename__       = "video"
	id                  = Column(id_type, primary_key=True)
	bee_record_id       = Column(id_type, ForeignKey("bee_record.id"), index=True)
	user_id             = Column(String, ForeignKey("user.id"))
	path                = Column(String)


class News(Base):
	__tablename__       = "video"
	id                  = Column(id_type, primary_key=True)
	user_id             = Column(String, ForeignKey("user.id"), index=True)
	news_type           = Column(Enum("main", "bio_cs", name="news_type"))
	content             = Column(JSON)


Base.metadata.create_all(db.engine)
