from typing import List

import pandas as pd
from geoalchemy2.shape import to_shape
from shapely import geometry

from beecology_api.db import BeeRecord
from beecology_api.serialization import bee_record_schema


# TODO Do something marshmallow-y with this?
def convert_dataframe(records: List[BeeRecord]) -> pd.DataFrame:
	"""Convert a dataframe of serialized bee records into an analysis-script format dataframe"""
	df = pd.DataFrame([{
			"time": pd.Timestamp(record.time).value if record.time is not None else None, # timestamp.value? shoot me
			"latitude": geometry.mapping(to_shape(record.location))["coordinates"][0] if record.location is not None else None,
			"longitude": geometry.mapping(to_shape(record.location))["coordinates"][1] if record.location is not None else None,
			"elevation": record.elevation,
			"species": record.bee_species.species if record.bee_species is not None else None,
			"behavior": record.behavior,
			"head_coloration": record.head_coloration,
			"abdomen_color": record.abdomen_coloration,
			"how_submitted": record.how_submitted,
			"submitted": pd.Timestamp(record.submitted).value if record.submitted is not None else None,
			"thorax_coloration": record.thorax_coloration,
			"flower_species": ("{} {}".format(record.flower_species.genus, record.flower_species.species)) if record.flower_species is not None else None
		} for record in records])

	return df
