from typing import List

from hiking.collection import HikeCollection
from hiking.models import Hike, session
from hiking.utils import SlimDateRange


def get_filtered_query(
    ids: List[int],
    daterange: "SlimDateRange",
):
    query = (
        session.query(Hike)
        .filter(Hike.date >= daterange.lower)
        .filter(Hike.date <= daterange.upper)
    )
    if ids:
        query = query.filter(Hike.id.in_(ids))
    return query


def get_collection(
    ids: List[int],
    daterange: "SlimDateRange",
):
    query = get_filtered_query(ids, daterange)
    collection = HikeCollection(hikes=query, session=session)
    return collection
