import datetime
from dataclasses import dataclass
from typing import Union

from sqlalchemy import Interval, func
from sqlalchemy.orm import Query

from hiking.models import Hike
from hiking.utils import format_value


@dataclass
class HikeCollection:
    hikes: Query

    def get_hikes_attr_list(
        self, attr: str
    ) -> list[Union[float, int, datetime.date, datetime.timedelta]]:
        return [getattr(hike, attr) for hike in self.hikes.all()]

    def sum(self, attr: str) -> Union[float, int, datetime.date, datetime.timedelta]:
        is_interval = isinstance(getattr(Hike, attr).expression.type, Interval)
        if getattr(Hike, attr).info["calculated_value"] or is_interval:
            attr_list = self.get_hikes_attr_list(attr)
            if is_interval:
                return sum(attr_list, datetime.timedelta())

            return sum(attr_list)  # pragma: no cover

        return self.hikes.with_entities(func.sum(getattr(Hike, attr))).scalar()

    def avg(self, attr: str) -> Union[float, datetime.timedelta]:
        if attr == "duration":
            return (
                sum([h.duration for h in self.hikes.all()], datetime.timedelta())
                / self.hikes.count()
            )
        if attr == "speed":
            return sum(getattr(h, attr) for h in self.hikes.all()) / self.hikes.count()

        return self.hikes.with_entities(func.avg(getattr(Hike, attr))).scalar()

    def max(self, attr: str) -> Union[float, int, datetime.date, datetime.timedelta]:
        if attr == "speed":
            return sorted(self.hikes.all(), key=lambda x: x.speed, reverse=True)[
                0
            ].speed

        return getattr(
            self.hikes.order_by(getattr(Hike, attr).desc()).limit(1).first(), attr
        )

    def min(self, attr: str) -> Union[float, int, datetime.date, datetime.timedelta]:
        if attr == "speed":
            return sorted(self.hikes.all(), key=lambda x: x.speed)[0].speed

        return getattr(
            self.hikes.order_by(getattr(Hike, attr).asc()).limit(1).first(), attr
        )

    def get_hikes_stats(self, order_params: tuple[str, bool]) -> list[list[str]]:
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

    def get_totals(self) -> list[str]:
        def get_summary_cell(attr: str, supported_calculations: list[str]):
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

        return [
            "",
            "STATS",
            str(self.hikes.count()),
            *[
                get_summary_cell(
                    field.info["name"], field.info["supported_calculations"]
                )
                for field in Hike.FIELDS
                if field.info["supported_calculations"]
            ],
        ]

    def get_collection_stats(
        self, order_params: tuple[str, bool], add_totals: bool = True
    ) -> tuple[list, list]:
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
            f"total {self.calc_and_format_value('sum', 'distance')} km>"
        )

    def __repr__(self) -> str:
        return self.__str__()
