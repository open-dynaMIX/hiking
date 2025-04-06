import json
import sys
import tempfile
from pathlib import Path

import pytest
from pytest_factoryboy.fixture import register

from hiking import __main__, factories
from hiking.collection import HikeCollection
from hiking.db_utils import session
from hiking.models import Hike, create_tables, get_filtered_query
from hiking.utils import setup_logging

OWN_DIR = Path(__file__).resolve().parent
GPX_TEST_FILE = OWN_DIR / "tests" / "data" / "test.gpx"
JSON_IMPORT_FILE = OWN_DIR / "tests" / "data" / "test_import.json"


register(factories.HikeFactory)


@pytest.fixture(scope="session", autouse=True)
def setup_db():
    create_tables()


@pytest.fixture(autouse=True)
def clear_db():
    try:
        yield
    finally:
        session.query(Hike).delete()
        session.commit()


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
        return f.read()


@pytest.fixture
def gpx_file():
    return GPX_TEST_FILE


@pytest.fixture
def json_import_data():
    with JSON_IMPORT_FILE.open("r") as f:
        return json.loads(f.read())


@pytest.fixture
def json_file():
    return JSON_IMPORT_FILE


@pytest.fixture
def export_dir():
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


@pytest.fixture
def collection(hike_factory):
    hike_factory.create_batch(3)
    return HikeCollection(get_filtered_query())


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
