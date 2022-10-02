import datetime
import os
from decimal import Decimal
from typing import List, Optional, Union

import plotille

from hiking.utils import format_value, pretty_timedelta


def plot(
    x: List[Union[datetime.date, Decimal, int, datetime.timedelta, float]],
    y: List[Union[datetime.date, Decimal, int, datetime.timedelta, float]],
    xlabel: Optional[str],
    ylabel: Optional[str],
    height: int = 20,
    x_limit_min: Optional[
        Union[datetime.date, Decimal, int, datetime.timedelta, float]
    ] = None,
    x_limit_max: Optional[
        Union[datetime.date, Decimal, int, datetime.timedelta, float]
    ] = None,
    y_limit_min: Optional[
        Union[datetime.date, Decimal, int, datetime.timedelta, float]
    ] = None,
    y_limit_max: Optional[
        Union[datetime.date, Decimal, int, datetime.timedelta, float]
    ] = None,
):
    x_type = type(x[0])
    y_type = type(y[0])

    def handle_ticks(tick: Union[float, datetime.date], _type: type):
        if _type == datetime.timedelta and isinstance(tick, float):
            return pretty_timedelta(datetime.timedelta(seconds=tick))
        elif _type == datetime.date and isinstance(tick, datetime.date):
            return tick.strftime("%m-%d")
        elif _type == int:
            return format_value(tick, "elevation_gain")
        elif _type == float:
            # setting to `speed` will get the right formatting
            return format_value(tick, "speed")
        return tick

    def set_yticks(tick, arg2):
        return handle_ticks(tick, y_type)

    def set_xticks(tick, arg2):
        return handle_ticks(tick, x_type)

    # plotille only allows for setting the plot width, but will add 33 more chars
    # to its output
    plot_width = max(os.get_terminal_size().columns - 33, 47)

    fig = plotille.Figure()
    fig.y_ticks_fkt = set_yticks
    fig.x_ticks_fkt = set_xticks
    fig.set_x_limits(min_=x_limit_min, max_=x_limit_max)
    fig.set_y_limits(min_=y_limit_min, max_=y_limit_max)
    fig.width = plot_width
    fig.height = height
    fig.x_label = xlabel
    fig.y_label = ylabel

    conversion_map = {
        Decimal: lambda v: float(v),
        datetime.timedelta: lambda v: v.total_seconds(),
        int: lambda v: v,
        datetime.date: lambda v: v,
        float: lambda v: v,
    }

    x = [conversion_map[type(i)](i) for i in x]
    y = [conversion_map[type(i)](i) for i in y]

    fig.color_mode = "rgb"
    fig.plot(x, y, lc=[82, 47, 112], label="square")
    fig.scatter(x, y, lc=[6, 150, 45], label="scatter")
    return fig.show()
