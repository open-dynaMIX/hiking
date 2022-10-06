import datetime

import factory.fuzzy

from hiking.db_utils import session
from hiking.models import Hike


class HikeFactory(factory.alchemy.SQLAlchemyModelFactory):
    id = None
    name = factory.Faker("name")
    body = factory.Faker("paragraph")
    date = factory.Faker("date_object")
    distance = factory.fuzzy.FuzzyFloat(5.0, 40.0)
    elevation_gain = factory.fuzzy.FuzzyInteger(200, 3500)
    elevation_loss = factory.fuzzy.FuzzyInteger(200, 3500)
    duration = factory.fuzzy.FuzzyChoice(
        [
            datetime.timedelta(minutes=i)
            for i in [45, 60, 75, 90, 105, 120, 135, 150, 165, 180]
        ]
    )
    gpx_xml = None

    class Meta:
        model = Hike
        sqlalchemy_session = session
        sqlalchemy_session_persistence = "commit"
