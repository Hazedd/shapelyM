from __future__ import annotations

from shapelyM.helpers import point_on_line
from shapelyM.measurePoint import MeasurePoint


def linear_reference_point_on_line(a: MeasurePoint, b: MeasurePoint, p: MeasurePoint):
    if a.z is not None and b.z is not None and p.z is not None:
        point_on_line_2d = point_on_line(
            MeasurePoint(a.x, a.y), MeasurePoint(b.x, b.y), MeasurePoint(p.x, p.y)
        )
        point = MeasurePoint(point_on_line_2d[0], point_on_line_2d[1])
        start_distance = point.distance(a, force_2d=True)
        end_distance = a.distance(b, force_2d=True)
        try:
            percentage = start_distance / end_distance
        except ZeroDivisionError:
            percentage = 0

        point.z = a.z + ((b.z - a.z) * percentage)
        return point_on_line(a, b, point)
    else:
        return point_on_line(a, b, p)
