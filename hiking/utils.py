import datetime
import os
from collections import namedtuple
from pathlib import Path
from typing import Optional, Union

from rich import box
from rich.console import Console

DATA_HOME = (
    Path(os.getenv("XDG_DATA_HOME")) / "hiking"
    if os.getenv("XDG_DATA_HOME")
    else Path.home() / ".local" / "share" / "hiking"
)

DB_PATH = DATA_HOME / "hikes.sqlite"
EDITOR = os.environ.get("EDITOR", "vi")
GPX_VIEWER = "/usr/bin/gpxsee"
DEFAULT_BOX_STYLE = box.HORIZONTALS
console = Console()


def pretty_timedelta(value: datetime.timedelta) -> str:
    hours = str(int(value.total_seconds() // 3600)).rjust(2, "0")
    minutes = str(int((value.total_seconds() // 60) % 60)).rjust(2, "0")
    return f"{hours}:{minutes}"


def format_value(
    value: Union[str, datetime.timedelta, datetime.date, float],
    attr: Optional[str] = None,
) -> str:
    if isinstance(value, datetime.timedelta):
        return pretty_timedelta(value)
    elif isinstance(value, datetime.date):
        return str(value)
    elif isinstance(value, str):
        return value

    assure_decimal_places = 0
    round_to_decimal_places = 2
    if attr and attr in ["elevation_gain", "elevation_loss"]:
        round_to_decimal_places = 0
    elif attr and attr == "distance":
        round_to_decimal_places = 1
        assure_decimal_places = 1
    elif attr and attr == "speed":
        assure_decimal_places = 2

    strs = str(round(value, round_to_decimal_places)).split(".")
    if len(strs) == 1:
        strs.append("")
    strs[1] = strs[1].rstrip("0")
    if len(strs[1]) < assure_decimal_places:
        strs[1] += "".ljust(assure_decimal_places - len(strs[1]), "0")
    return ".".join(strs) if strs[1] else strs[0]


SlimDateRange = namedtuple("SlimDateRange", ["lower", "upper"])
