import datetime
from collections import namedtuple
from typing import List, Optional

import gpxpy
from sqlalchemy import Column, Date, Float, Integer, Interval, String, Text
from sqlalchemy.orm import load_only

from hiking.db_utils import Base, engine, session
from hiking.utils import SlimDateRange, format_value, pretty_timedelta


def create_tables():
    Base.metadata.create_all(engine)


CalculatedField = namedtuple("CalculatedField", ["info"])


def info_dict(
    name: str,
    pretty_name: str,
    supported_calculations: Optional[List[str]] = None,
    data_view: bool = True,
    calculated_value: bool = False,
):
    return {
        "name": name,
        "pretty_name": pretty_name,
        "supported_calculations": supported_calculations or [],
        "data_view": data_view,
        "calculated_value": calculated_value,
    }


class Hike(Base):
    __tablename__ = "hikes"

    id = Column(
        Integer,
        primary_key=True,
        info=info_dict(name="id", pretty_name="ID"),
    )
    date = Column(
        Date,
        nullable=False,
        info=info_dict(name="date", pretty_name="Date"),
    )
    name = Column(
        String,
        nullable=False,
        info=info_dict(name="name", pretty_name="Name"),
    )
    body = Column(
        Text,
        nullable=True,
        info=info_dict(name="body", pretty_name="Body", data_view=False),
    )
    distance = Column(
        Float,
        nullable=False,
        info=info_dict(
            name="distance",
            pretty_name="➡ km",
            supported_calculations=["sum", "avg", "min", "max"],
        ),
    )
    elevation_gain = Column(
        Integer,
        nullable=False,
        info=info_dict(
            name="elevation_gain",
            pretty_name="⬈ m",
            supported_calculations=["sum", "avg", "min", "max"],
        ),
    )
    elevation_loss = Column(
        Integer,
        nullable=False,
        info=info_dict(
            name="elevation_loss",
            pretty_name="⬊ m",
            supported_calculations=["sum", "avg", "min", "max"],
        ),
    )
    duration = Column(
        Interval,
        nullable=False,
        info=info_dict(
            name="duration",
            pretty_name="⏱ ",
            supported_calculations=["sum", "avg", "min", "max"],
        ),
    )
    gpx_xml = Column(
        Text,
        info=info_dict(
            name="gpx",
            pretty_name="GPX",
            data_view=False,
        ),
    )

    FIELDS = [
        id,
        date,
        name,
        body,
        distance,
        elevation_gain,
        elevation_loss,
        duration,
        gpx_xml,
        CalculatedField(
            info=info_dict(
                name="speed",
                pretty_name="km/h",
                supported_calculations=["avg", "min", "max"],
                calculated_value=True,
            )
        ),
    ]

    _gpx = None

    @property
    def speed(self):
        return self.distance * 60 / (self.duration.seconds / 60)

    @property
    def gpx(self):
        if self.gpx_xml and not self._gpx:
            self._gpx = gpxpy.parse(self.gpx_xml)
        return self._gpx

    def get_pretty_value(
        self,
        attr: str,
    ):
        value = getattr(self, attr)
        return format_value(value, attr)

    def get_stats(self) -> List[str]:
        serialized = []
        for field in self.FIELDS:
            if not field.info["data_view"]:
                continue

            value = self.get_pretty_value(field.info["name"])
            serialized.append(value)

        return serialized

    def get_detail_stats(self) -> dict:
        serialized = {}
        for field in self.FIELDS:
            if not field.info["data_view"]:
                continue
            value = getattr(self, field.info["name"])
            if isinstance(value, datetime.timedelta):
                value = pretty_timedelta(value)
            elif field.info["name"] == "speed":
                value = round(value, 2)
            serialized[field.info["pretty_name"]] = value

        return serialized

    def load_gpx(self, gpx: str):
        gpx_obj = gpxpy.parse(gpx)

        data = {
            "date": gpx_obj.time.date() if gpx_obj.time else None,
            "name": gpx_obj.name,
            "distance": round(gpx_obj.length_3d() / 1000, 2),
            "elevation_gain": round(gpx_obj.get_uphill_downhill().uphill),
            "elevation_loss": round(gpx_obj.get_uphill_downhill().downhill),
            "duration": gpx_obj.get_duration(),
            "gpx_xml": gpx,
        }
        for attr, value in data.items():
            if value:
                setattr(self, attr, value)

    def save(self):
        if self.id is None:
            session.add(self)
        return session.commit()

    def delete(self):
        session.delete(self)
        return session.commit()

    def __str__(self) -> str:
        return f"<Hike - {self.name} - {self.date} - {self.distance} km>"

    def __repr__(self) -> str:
        return self.__str__()


def get_filtered_query(
    ids: Optional[List[int]] = None,
    daterange: Optional["SlimDateRange"] = None,
    load_all_columns: bool = False,
):
    query = session.query(Hike)
    if daterange:
        query = query.filter(Hike.date >= daterange.lower).filter(
            Hike.date <= daterange.upper
        )
    if ids:
        query = query.filter(Hike.id.in_(ids))

    # Only fetch columns needed for tabular stats
    if not load_all_columns:
        query = query.options(
            load_only(
                Hike.id,
                Hike.name,
                Hike.date,
                Hike.distance,
                Hike.elevation_gain,
                Hike.elevation_loss,
                Hike.duration,
            )
        )

    return query
