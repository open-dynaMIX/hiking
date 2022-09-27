import datetime
from dataclasses import dataclass
from typing import List, Tuple, Union

from sqlalchemy import Interval, desc, func
from sqlalchemy.orm import Query, Session

from hiking.models import Hike, Hike as HikeModel, session
from hiking.utils import format_value


@dataclass
class HikeCollection:
    hikes: Query
    session: Session

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

            return sum(attr_list)

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

    def longest_name_count(self) -> int:
        longest = self.hikes.order_by(desc(func.length(HikeModel.name))).first()
        return len(longest.name)

    def get_hikes_stats(self, order_params: Tuple[str, bool]) -> List[List[str]]:
        order = getattr(Hike, order_params[0])
        if order_params[1]:
            order = order.desc()
        query = self.hikes.order_by(order)
        return [hike.get_stats() for hike in query]

    def calc_and_format_value(self, calc: str, attr: str) -> str:
        result = getattr(self, calc)(attr)
        return format_value(result, attr)

    def get_divider(self) -> List[str]:
        return [
            "=" * (2 + len(self.calc_and_format_value("max", "id"))),
            "=" * 10,
            "=" * self.longest_name_count(),
            "=" * (3 + len(self.calc_and_format_value("sum", "distance"))),
            "=" * (3 + len(self.calc_and_format_value("sum", "elevation_gain"))),
            "=" * (3 + len(self.calc_and_format_value("sum", "elevation_loss"))),
            "=" * (3 + len(self.calc_and_format_value("sum", "duration"))),
            "=" * (3 + len(self.calc_and_format_value("max", "speed"))),
        ]

    def get_totals(self) -> List[str]:
        d = [
            "",
            "STATS",
            str(self.hikes.count()),
            *(
                "".join(
                    (
                        f"{pretty_calc}: {self.calc_and_format_value(calc, attr)}{opt_newline}"
                        if calc in config["supported_calculations"]
                        else "-\n"
                        for calc, pretty_calc, opt_newline in [
                            ("sum", "Σ", "\n"),
                            ("avg", "⌀", "\n"),
                            ("max", "↑", "\n"),
                            ("min", "↓", ""),
                        ]
                    )
                )
                for attr, config in Hike.FIELD_PROPS.items()
                if config["supported_calculations"]
            ),
        ]
        return d

    def get_collection_stats(
        self, order_params: Tuple[str, bool], add_totals: bool = True
    ) -> Tuple[List[List[str]], List[str]]:
        stats = self.get_hikes_stats(order_params)

        result = [
            *stats,
        ]

        footer = None
        if add_totals and len(stats) > 1:
            # Only add stats if more than one hike is present
            # result.append(self.get_divider())
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
