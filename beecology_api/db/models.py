from datetime import datetime

from geoalchemy2 import Geometry
from sqlalchemy import Column, String, DateTime, Enum, Float, ForeignKey, Boolean, Text, JSON
from sqlalchemy.dialects import postgresql
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from beecology_api import config

"""Core SQLAlchemy ORM mappings for objects to tables"""
months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November",
          "December"]
genders = ["male", "female", "queen", "male/female", "worker"]
beehaviors = ["pollen", "nectar", "unknown"]
tongue_lengths = ["long", "medium", "short"]
news_types = ["biocs", "main"]

use_postgres = "postgres" in config.config["database"]["connection"]
id_type = postgresql.UUID(as_uuid=True) if use_postgres else String
array_type = postgresql.ARRAY(String) if use_postgres else String
BaseTable = declarative_base()


class User(BaseTable):
	__tablename__ = "user"
	id = Column(String, primary_key=True, index=True)
	admin = Column(Boolean, default=False)
	locked = Column(Boolean, default=False)
	registration_date = Column(DateTime(timezone=True), default=datetime.now())
	last_login = Column(DateTime, default=datetime.now())
	records = relationship("BeeRecord")
	media = relationship("Media")
	news = relationship("News")


class BeeRecord(BaseTable):
	__tablename__ = "bee_flower_observation"
	id = Column(id_type, primary_key=True, index=True)
	user_id = Column(String, ForeignKey("user.id", ondelete="SET NULL"), index=True)
	bee_species_id = Column(id_type, ForeignKey("bee_species.id"), index=True, nullable=True)
	flower_species_id = Column(id_type, ForeignKey("flower_species.id"), index=True, nullable=True)
	bee_species = relationship("BeeSpecies", backref="records", lazy="joined")
	flower_species = relationship("FlowerSpecies", backref="records", lazy="joined")
	abdomen_coloration = Column(String)
	thorax_coloration = Column(String)
	head_coloration = Column(String)
	gender = Column(Enum(*genders, name="bee_gender"))
	behavior = Column(Enum(*beehaviors, name="bee_behavior"))
	time = Column(DateTime(timezone=True))
	submitted = Column(DateTime(timezone=True), server_default=func.now())
	location = Column(Geometry(geometry_type="POINT", spatial_index=True) if use_postgres else String)
	elevation = Column(Float)
	closest_city = Column(String)
	media = relationship("Media", backref="bee_flower_observation")
	how_submitted = Column(Enum("webapp", "androidapp", "museum", "expert", name="submission_type"))


class BeeSpecies(BaseTable):
	__tablename__ = "bee_species"
	id = Column(id_type, primary_key=True, index=True)
	# genus = Column(String)
	species = Column(String)
	common_names = Column(array_type)
	description = Column(Text)
	tongue_length = Column(Enum(*tongue_lengths, name="tongue_length"))
	active_start = Column(String)
	active_end = Column(String)
	confused_with = Column(array_type)
	image = Column(String)


class FlowerSpecies(BaseTable):
	__tablename__ = "flower_species"
	id = Column(id_type, primary_key=True, index=True)
	genus = Column(String)
	species = Column(String)
	common_name = Column(String)
	alt_names = Column(array_type)
	main_color = Column(String)
	colors = Column(array_type)
	bloom_start = Column(String)
	bloom_end = Column(String)
	shape = Column(String)
	image = Column(String)


class Media(BaseTable):
	__tablename__ = "media"
	id = Column(id_type, primary_key=True)
	bee_flower_observation_id = Column(id_type, ForeignKey("bee_flower_observation.id"), index=True, nullable=True)
	user_id = Column(String, ForeignKey("user.id"))
	uploaded = Column(DateTime(timezone=True), server_default=func.now())
	web_path = Column(String)
	file_path = Column(String)
	type = Column(Enum("image", "video", name="media_type"))


class News(BaseTable):
	__tablename__ = "news"
	id = Column(id_type, primary_key=True)
	user_id = Column(String, ForeignKey("user.id"), index=True, nullable=True)
	type = Column(Enum(*news_types, name="news_type"))
	posted = Column(DateTime(timezone=True), index=True)
	content = Column(JSON)
