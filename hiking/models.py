import datetime
import os
from typing import List

import gpxpy
from sqlalchemy import (
    Column,
    Date,
    Float,
    Integer,
    Interval,
    String,
    Text,
    create_engine,
)
from sqlalchemy.orm import declarative_base, sessionmaker

from hiking.utils import DB_PATH, format_value, pretty_timedelta

Base = declarative_base()
engine = create_engine(
    f"sqlite:///{str(DB_PATH.absolute())}"
    if not os.environ.get("HIKING_TEST")
    else "sqlite://"  # , echo=True
)
Session = sessionmaker(bind=engine)
session = Session()


def create_tables():
    Base.metadata.create_all(engine)


class Hike(Base):
    __tablename__ = "hikes"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    body = Column(Text, nullable=True)
    date = Column(Date, nullable=False)
    distance = Column(Float, nullable=False)
    elevation_gain = Column(Integer, nullable=False)
    elevation_loss = Column(Integer, nullable=False)
    duration = Column(Interval, nullable=False)
    gpx_xml = Column(Text)

    FIELD_PROPS = {
        "id": {
            "pretty_name": "ID",
            "supported_calculations": [],
            "data_view": True,
            "calculated_value": False,
        },
        "date": {
            "pretty_name": "Date",
            "supported_calculations": [],
            "data_view": True,
            "calculated_value": False,
        },
        "name": {
            "pretty_name": "Name",
            "supported_calculations": [],
            "data_view": True,
            "calculated_value": False,
        },
        "body": {
            "pretty_name": "Body",
            "supported_calculations": [],
            "data_view": False,
            "calculated_value": False,
        },
        "distance": {
            "pretty_name": "➡ km",
            "supported_calculations": ["sum", "avg", "min", "max"],
            "data_view": True,
            "calculated_value": False,
        },
        "elevation_gain": {
            "pretty_name": "⬈ m",
            "supported_calculations": ["sum", "avg", "min", "max"],
            "data_view": True,
            "calculated_value": False,
        },
        "elevation_loss": {
            "pretty_name": "⬊ m",
            "supported_calculations": ["sum", "avg", "min", "max"],
            "data_view": True,
            "calculated_value": False,
        },
        "duration": {
            "pretty_name": "⏱ ",
            "supported_calculations": ["sum", "avg", "min", "max"],
            "data_view": True,
            "calculated_value": False,
        },
        "speed": {
            "pretty_name": "km/h",
            "supported_calculations": ["avg", "min", "max"],
            "data_view": True,
            "calculated_value": True,
        },
        "gpx": {
            "pretty_name": "GPX",
            "supported_calculations": [],
            "data_view": False,
            "calculated_value": False,
        },
    }

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
        for attr, config in self.FIELD_PROPS.items():
            if not config["data_view"]:
                continue

            value = self.get_pretty_value(attr)
            serialized.append(value)

        return serialized

    def get_detail_stats(self) -> dict:
        serialized = {}
        for f, config in self.FIELD_PROPS.items():
            if not config["data_view"]:
                continue
            value = getattr(self, f)
            if isinstance(value, datetime.timedelta):
                value = pretty_timedelta(value)
            elif f == "speed":
                value = round(value, 2)
            serialized[config["pretty_name"]] = value

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
        return f"<Hike - {self.name} - {self.date} - {self.distance}km>"

    def __repr__(self) -> str:
        return self.__str__()
