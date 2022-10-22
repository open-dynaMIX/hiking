import datetime
import json
from pathlib import Path
from typing import List

import gpxpy
import sqlalchemy.orm
from gpxpy.gpx import GPXException

from hiking.db_utils import session
from hiking.exceptions import HikingJsonLoaderException
from hiking.models import Hike


def validate_json_obj(hike_data: dict):
    expected_fields = {
        "name",
        "date",
        "distance",
        "elevation_gain",
        "elevation_loss",
        "duration",
        "gpx_file",
    }
    fields_not_present = sorted(expected_fields - set(hike_data.keys()))
    fields_unknown = sorted(set(hike_data.keys()) - expected_fields)

    if fields_not_present or (
        fields_unknown
        and sorted(fields_unknown) not in [["id"], ["body"], ["body", "id"]]
    ):
        msg = "Invalid JSON data:"
        if fields_not_present:
            msg = f"{msg}\nMissing fields: {', '.join(fields_not_present)}"
        if fields_unknown:
            msg = f"{msg}\nUnknown fields: {', '.join(fields_unknown)}"
        raise HikingJsonLoaderException(msg)


def json_importer(json_data: List[dict]):
    to_add = []
    to_merge = []
    for raw_hike in json_data:
        validate_json_obj(raw_hike)

        try:
            raw_hike["date"] = datetime.datetime.strptime(
                raw_hike["date"], "%Y-%m-%d"
            ).date()
        except ValueError:
            raise HikingJsonLoaderException("Wrong date format")
        try:
            raw_hike["duration"] = datetime.timedelta(minutes=raw_hike["duration"])
        except TypeError:
            raise HikingJsonLoaderException("Wrong duration format")
        if raw_hike["gpx_file"]:
            gpx_file = Path(raw_hike["gpx_file"])
            if not gpx_file.is_file() or not gpx_file.exists():
                raise HikingJsonLoaderException(
                    f'*.gpx file "{raw_hike["gpx_file"]}" not found'
                )
            with gpx_file.open("r") as f:
                gpx_xml = f.read()
            try:
                gpxpy.parse(gpx_xml)
            except GPXException as e:
                raise HikingJsonLoaderException(e.args[0])

            raw_hike["gpx_xml"] = gpx_xml
        raw_hike.pop("gpx_file")

        if raw_hike.get("id") is not None:
            to_merge.append(raw_hike)
            continue
        to_add.append(raw_hike)

    session.bulk_insert_mappings(Hike, to_add)
    session.bulk_update_mappings(Hike, to_merge)
    session.commit()


def json_exporter(
    query: sqlalchemy.orm.Query, export_dir: Path, include_ids: bool = False
):
    data = []
    gpx_dir = export_dir / "gpx"
    for hike in query:
        hike_data = {
            "name": hike.name,
            "body": hike.body,
            "date": str(hike.date),
            "distance": hike.distance,
            "elevation_gain": hike.elevation_gain,
            "elevation_loss": hike.elevation_loss,
            "duration": round(hike.duration.total_seconds() / 60),
            "gpx_file": None,
        }
        if include_ids:
            hike_data["id"] = hike.id

        if hike.gpx_xml:
            gpx_dir.mkdir(exist_ok=True)
            gpx_file = gpx_dir / f"{str(hike.id)}.gpx"
            with open(gpx_file, "w") as f:
                f.write(hike.gpx_xml)
            hike_data["gpx_file"] = str(gpx_file.absolute())
        data.append(hike_data)

    with (export_dir / "hikes.json").open("w") as f:
        f.write(json.dumps(data, indent=4))


JSON_IMPORT_EXAMPLE = json.dumps(
    [
        {
            "id": "$Integer (optional; update if present)",
            "name": "$String",
            "body": "$String",
            "date": "YYY-MM-DD",
            "distance": "$Foat",
            "elevation_gain": "$Integer",
            "elevation_loss": "$Integer",
            "duration": "$Integer",
            "gpx": "$String (path to file; optional)",
        }
    ],
    indent=4,
)
