import datetime
import json
import sys
import tempfile
from pathlib import Path

import pytest
from pytest_factoryboy.fixture import register

from hiking import __main__, factories
from hiking.collection import HikeCollection
from hiking.db_utils import engine, session
from hiking.models import create_tables, get_filtered_query
from hiking.utils import setup_logging

OWN_DIR = Path(__file__).resolve().parent
GPX_TEST_FILE = OWN_DIR / "tests" / "data" / "test.gpx"
JSON_IMPORT_FILE = OWN_DIR / "tests" / "data" / "test_import.json"


register(factories.HikeFactory)


@pytest.fixture(scope="session", autouse=True)
def setup_db():
    create_tables()


@pytest.fixture(autouse=True)
def db():
    try:
        yield
    finally:
        with engine.connect() as con:
            con.execute("DELETE FROM hikes;")
        session.commit()
        session.close()
        session.begin()


@pytest.fixture
def debug_logging():
    setup_logging(debug=True)
    try:
        yield
    finally:
        setup_logging(debug=False)


@pytest.fixture
def unset_debug_logging():
    try:
        yield
    finally:
        setup_logging(debug=False)


@pytest.fixture
def gpx_xml():
    with GPX_TEST_FILE.open("r") as f:
        xml = f.read()
    return xml


@pytest.fixture
def gpx_file():
    return GPX_TEST_FILE


@pytest.fixture
def json_import_data():
    with JSON_IMPORT_FILE.open("r") as f:
        data = json.loads(f.read())
    return data


@pytest.fixture
def json_file():
    return JSON_IMPORT_FILE


@pytest.fixture
def export_dir():
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


@pytest.fixture
def collection(hike_factory):
    hike_factory(
        date=datetime.date(1984, 9, 22),
        name="Foo Hike",
        body="# Foo Hike",
        distance=10.5,
        elevation_gain=2040,
        elevation_loss=2028,
        duration=datetime.timedelta(minutes=134),
    )

    hike_factory(
        date=datetime.date(1984, 9, 23),
        name="Bar Hike",
        body="# Bar Hike",
        distance=15.4,
        elevation_gain=240,
        elevation_loss=228,
        duration=datetime.timedelta(minutes=228),
    )

    hike_factory(
        date=datetime.date(1984, 9, 24),
        name="Baz Hike",
        body="# Baz Hike",
        distance=34.0,
        elevation_gain=867,
        elevation_loss=947,
        duration=datetime.timedelta(minutes=497),
    )

    return HikeCollection(get_filtered_query())


@pytest.fixture
def known_hike(hike_factory):
    return hike_factory(
        date=datetime.date(1984, 9, 23),
        name="Foo Bar Hike",
        body="# Foo Bar Hike\n\nMy awesome journey...",
        distance=20.7,
        elevation_gain=2040,
        elevation_loss=2028,
        duration=datetime.timedelta(minutes=434),
    )


@pytest.fixture
def sys_argv():
    old_sys_argv = sys.argv
    try:
        yield sys.argv
    finally:
        sys.argv = old_sys_argv


@pytest.fixture(autouse=True)
def mock_data_home(mocker):
    mocker.patch.object(__main__, "DATA_HOME")
