import os

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from hiking.utils import DB_PATH

Base = declarative_base()
engine = create_engine(
    f"sqlite:///{str(DB_PATH.absolute())}"
    if not os.environ.get("HIKING_TEST")
    else "sqlite://"
)
Session = sessionmaker(bind=engine)
session = Session()
