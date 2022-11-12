import datetime
import random

import factory.fuzzy

from hiking.db_utils import session
from hiking.models import Hike


class HikeFactory(factory.alchemy.SQLAlchemyModelFactory):
    id = None
    name = factory.Faker("name")
    body = factory.Faker("paragraph")
    date = factory.Faker("date_object")
    distance = factory.fuzzy.FuzzyFloat(5.0, 40.0, precision=4)
    elevation_gain = factory.fuzzy.FuzzyInteger(200, 3500)
    elevation_loss = factory.fuzzy.FuzzyInteger(200, 3500)
    gpx_xml = None

    @factory.lazy_attribute
    def duration(self):
        # make sure generated hikes have a realistic speed
        speed = random.uniform(4.0, 5.5)
        return datetime.timedelta(hours=(self.distance / speed))

    class Meta:
        model = Hike
        sqlalchemy_session = session
        sqlalchemy_session_persistence = "commit"
