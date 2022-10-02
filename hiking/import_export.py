import datetime
import json
from pathlib import Path

import gpxpy
import sqlalchemy.orm

from hiking.exceptions import HikingJsonLoaderException
from hiking.models import Hike, session


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

    if fields_not_present or fields_unknown:
        msg = "Invalid JSON data:"
        if fields_not_present:
            msg = f"{msg}\nMissing fields: {', '.join(fields_not_present)}"
        if fields_unknown:
            msg = f"{msg}\nUnknown fields: {', '.join(fields_unknown)}"
        raise HikingJsonLoaderException(msg)


def json_importer(json_data: dict):
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
            assert gpxpy.parse(gpx_xml)
            raw_hike["gpx_xml"] = gpx_xml
        raw_hike.pop("gpx_file")
        hike = Hike(**raw_hike)
        session_method = "add"
        if hike.id and not isinstance(hike.id, int):
            raise HikingJsonLoaderException(
                f'*.gpx file "{raw_hike["gpx_file"]}" not found'
            )
        elif hike.id:
            session_method = "merge"

        getattr(session, session_method)(hike)
    session.commit()


def json_exporter(query: sqlalchemy.orm.Query, export_dir: Path):
    data = []
    gpx_dir = export_dir / "gpx"
    for hike in query:
        hike_data = {
            "id": hike.id,
            "name": hike.name,
            "body": hike.body,
            "date": str(hike.date),
            "distance": hike.distance,
            "elevation_gain": hike.elevation_gain,
            "elevation_loss": hike.elevation_loss,
            "duration": round(hike.duration.total_seconds() / 60),
            "gpx_file": None,
        }
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
