from typing import List

import pandas as pd
from geoalchemy2.shape import to_shape
from shapely import geometry

from beecology_api.db import BeeRecord


def _convert_gender(gender: str) -> str:
	"""Convert gender as stored in the database to gender as it should appear in the analysis and CSV files"""
	if gender == "worker" or gender == "queen":
		return "female"
	return gender

# TODO Do something marshmallow-y with this?
def convert_dataframe(records: List[BeeRecord], time_human_readable=False) -> pd.DataFrame:
	"""Convert a dataframe of serialized bee records into an analysis-script format dataframe"""
	dict_records = []
	for record in records:
		dict_record = {
			# "how_submitted": record.how_submitted,
			# "submitted": pd.Timestamp(record.submitted).value if record.submitted is not None else None,
			"time": (record.time.isoformat() if time_human_readable else record.time) if record.time is not None else None,  # timestamp.value? shoot me
			"year": record.time.year if record.time is not None else None,
			"month": record.time.month if record.time is not None else None,
			"day": record.time.day if record.time is not None else None,
			"latitude": geometry.mapping(to_shape(record.location))["coordinates"][0] if record.location is not None else None,
			"longitude": geometry.mapping(to_shape(record.location))["coordinates"][1] if record.location is not None else None,
			"elevation": record.elevation,
			"species": None,
			"behavior": record.behavior,
			"gender": _convert_gender(record.gender),
			"tongue_length": None,
			"bee_active_start": None,
			"bee_active_end": None,
			"flower_species": None,
			"flower_genus": None,
			"flower_common_name": None,
			"flower_main_color": None,
			"flower_shape": None,
			"flower_bloom_start": None,
			"flower_bloom_end": None
		}
		if record.bee_species is not None:
			s = record.bee_species
			dict_record["species"] = s.species
			dict_record["tongue_length"] = s.tongue_length
			dict_record["bee_active_start"] = s.active_start
			dict_record["bee_active_end"] = s.active_end
		if record.flower_species is not None:
			f = record.flower_species
			dict_record["flower_species"] = f.species
			dict_record["flower_genus"] = f.genus
			dict_record["flower_common_name"] = f.common_name
			dict_record["flower_main_color"] = f.main_color
			dict_record["flower_shape"] = f.shape
			dict_record["flower_bloom_start"] = f.bloom_start
			dict_record["flower_bloom_end"] = f.bloom_end

		dict_records.append(dict_record)

	return pd.DataFrame(dict_records)
