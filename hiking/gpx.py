from typing import TYPE_CHECKING

from geopy.distance import distance

from hiking.plot import plot

if TYPE_CHECKING:  # pragma: no cover
    from models import Hike


def get_elevation_profile(hike: "Hike"):
    if not hike.gpx:
        return "No *.gpx-file available"

    x = []
    y = []
    total_distance = 0
    old_point = None
    for track in hike.gpx.tracks:
        for segment in track.segments:
            for point in segment.points:
                if old_point is not None:
                    total_distance += distance(
                        (old_point.latitude, old_point.longitude),
                        (point.latitude, point.longitude),
                    ).meters
                x.append(total_distance / 1000)
                y.append(round(point.elevation))
                old_point = point
            old_point = None
        old_point = None

    return plot(x, y, x_limit_min=0, xlabel="Distance (km)", ylabel="elevation (m)")
