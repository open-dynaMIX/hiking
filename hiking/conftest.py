from pathlib import Path

import pytest
from pytest_factoryboy.fixture import register

from hiking import factories
from hiking.models import create_tables, engine, session

OWN_DIR = Path(__file__).resolve().parent
GPX_TEST_FILE = OWN_DIR / "tests" / "data" / "test.gpx"


register(factories.HikeFactory)


@pytest.fixture(scope="session", autouse=True)
def setup_db():
    create_tables()


@pytest.fixture(autouse=True)
def db():
    yield
    with engine.connect() as con:
        con.execute("DELETE FROM hikes;")
    session.commit()
    session.close()
    session.begin()


@pytest.fixture
def gpx_xml():
    with GPX_TEST_FILE.open("r") as f:
        xml = f.read()
    return xml
