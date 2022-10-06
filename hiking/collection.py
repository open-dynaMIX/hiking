import datetime
from dataclasses import dataclass
from typing import List, Tuple, Union

from sqlalchemy import Interval, func
from sqlalchemy.orm import Query

from hiking.db_utils import session
from hiking.models import Hike, get_filtered_query
from hiking.utils import SlimDateRange, format_value


@dataclass
class HikeCollection:
    hikes: Query

    def get_hikes_attr_list(
        self, attr: str
    ) -> List[Union[float, int, datetime.date, datetime.timedelta]]:
        return [getattr(hike, attr) for hike in self.hikes.all()]

    def sum(
        self, attr: str = "distance"
    ) -> Union[float, int, datetime.date, datetime.timedelta]:
        is_interval = isinstance(getattr(Hike, attr).expression.type, Interval)
        if Hike.FIELD_PROPS[attr]["calculated_value"] or is_interval:
            attr_list = self.get_hikes_attr_list(attr)
            if is_interval:
                return sum(attr_list, datetime.timedelta())

            return sum(attr_list)  # pragma: no cover

        result = session.query(func.sum(getattr(Hike, attr))).first()[0]
        return result

    def avg(self, attr: str = "distance") -> Union[float, datetime.timedelta]:
        if attr == "duration":
            return (
                sum([h.duration for h in self.hikes.all()], datetime.timedelta())
                / self.hikes.count()
            )
        return sum(getattr(h, attr) for h in self.hikes.all()) / self.hikes.count()

    def max(
        self, attr: str = "distance"
    ) -> Union[float, int, datetime.date, datetime.timedelta]:
        if attr == "speed":
            return sorted(self.hikes.all(), key=lambda x: x.speed, reverse=True)[
                0
            ].speed

        result = getattr(
            self.hikes.order_by(getattr(Hike, attr).desc()).limit(1).first(), attr
        )
        return result

    def min(
        self, attr: str = "distance"
    ) -> Union[float, int, datetime.date, datetime.timedelta]:
        if attr == "speed":
            return sorted(self.hikes.all(), key=lambda x: x.speed)[0].speed

        result = getattr(
            self.hikes.order_by(getattr(Hike, attr).asc()).limit(1).first(), attr
        )
        return result

    def get_hikes_stats(self, order_params: Tuple[str, bool]) -> List[List[str]]:
        if order_params[0] == "speed":
            hike_list = sorted(
                self.hikes.all(), key=lambda x: x.speed, reverse=order_params[1]
            )
            return [hike.get_stats() for hike in hike_list]

        order = getattr(Hike, order_params[0])
        if order_params[1]:
            order = order.desc()
        query = self.hikes.order_by(order)
        return [hike.get_stats() for hike in query]

    def calc_and_format_value(self, calc: str, attr: str) -> str:
        result = getattr(self, calc)(attr)
        return format_value(result, attr)

    def get_totals(self) -> List[str]:
        def get_summary_cell(attr: str, supported_calculations: List[str]):
            if supported_calculations:
                cell = {}
                for calc, pretty_calc in [
                    ("sum", "Σ "),
                    ("avg", "⌀ "),
                    ("max", "↑ "),
                    ("min", "↓ "),
                ]:
                    cell[pretty_calc] = "-"
                    if calc in supported_calculations:
                        cell[pretty_calc] = self.calc_and_format_value(calc, attr)
                return cell

        d = [
            "",
            "STATS",
            str(self.hikes.count()),
            *[
                get_summary_cell(attr, config["supported_calculations"])
                for attr, config in Hike.FIELD_PROPS.items()
                if config["supported_calculations"]
            ],
        ]
        return d

    def get_collection_stats(
        self, order_params: Tuple[str, bool], add_totals: bool = True
    ) -> Tuple[List, List]:
        stats = self.get_hikes_stats(order_params)

        result = [
            *stats,
        ]

        footer = None
        if add_totals and len(stats) > 1:
            # Only add totals if more than one hike is present
            footer = self.get_totals()

        return result, footer

    def __str__(self) -> str:
        return (
            f"<HikeCollection - "
            f"containing {self.hikes.count()} hikes - "
            f"total {self.sum()}km>"
        )

    def __repr__(self) -> str:
        return self.__str__()


def get_collection(
    ids: List[int],
    daterange: "SlimDateRange",
):
    query = get_filtered_query(ids, daterange)
    collection = HikeCollection(hikes=query)
    return collection
