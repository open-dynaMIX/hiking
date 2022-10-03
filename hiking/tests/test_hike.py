import datetime

import pytest
from gpxpy.gpx import GPX

from hiking.gpx import get_elevation_profile
from hiking.models import Hike, session


def test_hike(known_hike, snapshot):
    assert known_hike.speed == 2.8617511520737327
    assert known_hike.get_pretty_value("speed") == "2.86"

    assert known_hike.get_stats() == snapshot
    assert known_hike.get_detail_stats() == snapshot

    query = session.query(Hike)
    assert query.count() == 1
    assert session.query(Hike).first().name == known_hike.name
    known_hike.name = "new name"
    known_hike.save()
    assert session.query(Hike).first().name == "new name"


def test_hike_load_gpx(hike, gpx_xml):
    hike.load_gpx(gpx_xml)
    assert isinstance(hike.gpx, GPX)
    assert hike.name == hike.gpx.name
    assert hike.date == hike.gpx.time.date()
    assert hike.distance == round(hike.gpx.length_3d() / 1000, 2)
    assert hike.elevation_gain == round(hike.gpx.get_uphill_downhill().uphill)
    assert hike.elevation_loss == round(hike.gpx.get_uphill_downhill().downhill)
    assert hike.gpx_xml == gpx_xml
    # duration differs, because our test gpx file has no timestamps
    hike.save()


@pytest.mark.parametrize("add_gpx", [True, False])
def test_hike_gpx_elevation_profile(add_gpx, hike, gpx_xml, snapshot):
    if add_gpx:
        hike.gpx_xml = gpx_xml
        hike.save()

    ele_profile = get_elevation_profile(hike)
    assert ele_profile == snapshot


def test_hike_save_delete():
    hike = Hike(
        name="Foo",
        date=datetime.date(1999, 9, 9),
        distance=23.5,
        elevation_gain=123,
        elevation_loss=666,
        duration=datetime.timedelta(minutes=90),
    )
    q = session.query(Hike)
    assert q.count() == 0
    hike.save()
    assert q.count() == 1
    assert hike == q.first()
    hike.name = "Bar"
    hike.save()
    assert q.count() == 1
    assert q.first().name == "Bar"
    hike.delete()
    assert q.count() == 0
