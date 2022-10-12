from __future__ import annotations

from shapelyM.helpers import (
    MinimalPoint,
    PointProtocol,
    check_point_between_points,
    get_z_between_points,
    project_point_on_line,
)
from shapelyM.measurePoint import MeasurePoint


def _correct_overshoot(
    point_1: PointProtocol, point_2: PointProtocol, point_on_line_2d: PointProtocol
) -> MinimalPoint:
    # if not between we assume it overshoots
    if not check_point_between_points(point_1, point_2, point_on_line_2d):
        point_on_line_2d = MinimalPoint(point_2.x, point_2.y)
    return point_on_line_2d


def linear_reference_point_on_line(
    point_1: PointProtocol, point_2: PointProtocol, point_to_project: PointProtocol
) -> MeasurePoint:
    """Get 2d or 3d point between 2 points.

    :param point_1: shapely.geometry.Point or shapelyM.MeasurePoint
    :param point_2: shapely.geometry.Point or shapelyM.MeasurePoint
    :param point_to_project: shapely.geometry.Point or shapelyM.MeasurePoint

    """
    if point_1.z is not None and point_2.z is not None and point_to_project.z is not None:
        new_point = project_point_on_line(point_1, point_2, point_to_project)
        new_point = _correct_overshoot(point_1, point_2, new_point)
        new_point.z = get_z_between_points(point_1, point_2, new_point)
        return MeasurePoint(*new_point.coords)

    else:
        new_point = project_point_on_line(point_1, point_2, point_to_project)
        new_point = _correct_overshoot(point_1, point_2, new_point)
        return MeasurePoint(*new_point.coords)
