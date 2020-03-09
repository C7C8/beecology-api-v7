from geoalchemy2 import Geography
from geoalchemy2.shape import from_shape, to_shape
from marshmallow import fields
from marshmallow_sqlalchemy import ModelSchema, ModelConverter
from shapely import geometry

from beecology_api.db import *

"""Marshmallow de/serialization schemas and related converters"""


class _PointField(fields.Field):
	"""Marshmallow field to hold a point"""

	# Based upon https://gist.github.com/om-henners/97bc3a4c0b589b5184ba621fd22ca42e
	def _serialize(self, value, attr, obj, **kwargs):
		if value is None:
			return None
		point = geometry.mapping(to_shape(value))["coordinates"]
		return {"latitude": point[0], "longitude": point[1]}

	def _deserialize(self, value, attr, data, **kwargs):
		if value is None:
			return None
		return from_shape(geometry.Point(*value.values()))


class _MediaField(fields.Field):
	def __init__(self, table, **metadata):
		self.table = table
		super().__init__(**metadata)

	"""Marshmallow field for deserializing an image to just a path"""
	def _serialize(self, value, attr, obj, **kwargs):
		if value is None:
			return None
		return [{"path": media.client_path, "id": media.id} for media in value]

	def _deserialize(self, value, attr, data, **kwargs):
		if value is None:
			return None
		return self.parent.session.query(self.table).filter(self.table.id.in_(value)).all()


class Converter(ModelConverter):
	"""Converter to serialize or deserialize a point."""
	SQLA_TYPE_MAPPING = ModelConverter.SQLA_TYPE_MAPPING.copy()
	SQLA_TYPE_MAPPING.update({
		Geography: fields.Str
	})


class UserSchema(ModelSchema):
	class Meta:
		model = User


class BeeRecordSchema(ModelSchema):
	location = _PointField(attribute="location")
	media = _MediaField(table=Media, attribute="images")

	class Meta:
		model = BeeRecord
		model_converter = Converter
		include_fk = True


class BeeSpeciesSchema(ModelSchema):
	class Meta:
		model = BeeSpecies
		include_fk = True


class FlowerSpeciesSchema(ModelSchema):
	class Meta:
		model = FlowerSpecies
		include_fk = True


class NewsSchema(ModelSchema):
	class Meta:
		model = News
		include_fk = True


class MediaSchema(ModelSchema):
	class Meta:
		model = Media


user_schema = UserSchema()
bee_record_schema = BeeRecordSchema(exclude=["user_id"])
bee_species_schema = BeeSpeciesSchema()
flower_species_schema = FlowerSpeciesSchema()
news_schema = NewsSchema(exclude=["user_id"])
media_schema = MediaSchema(exclude=["file_path"])
