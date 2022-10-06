from typing import TYPE_CHECKING

from hiking.plot import plot

if TYPE_CHECKING:  # pragma: no cover
    from models import Hike


def get_elevation_profile(hike: "Hike"):
    if not hike.gpx:
        return "No *.gpx-file available"

    x = []
    y = []
    for point in hike.gpx.get_points_data():
        x.append(point.distance_from_start / 1000)
        y.append(round(point.point.elevation))

    return plot(x, y, x_limit_min=0, xlabel="Distance (km)", ylabel="elevation (m)")
