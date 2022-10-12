from __future__ import annotations

from shapelyM.helpers import check_point_between_points, project_point_on_line, PointProtocol, MinimalPoint
from shapelyM.measurePoint import MeasurePoint


def _correct_overshoot(
    point_1: PointProtocol, point_2: PointProtocol, point_on_line_2d: PointProtocol
) -> MinimalPoint:
    # if not between we assume it overshoots
    if not check_point_between_points(point_1, point_2, point_on_line_2d):
        point_on_line_2d = MinimalPoint(point_2.x, point_2.y)
    return point_on_line_2d


def _set_z_on_percentage(point_1, point_2, point_on_line_2d) -> MeasurePoint:
    point = MeasurePoint(point_on_line_2d.x, point_on_line_2d.y)
    start_distance = point.distance(point_1, force_2d=True)
    end_distance = point_1.distance(point_2, force_2d=True)
    try:
        percentage = start_distance / end_distance
    except ZeroDivisionError:
        percentage = 0

    point.z = point_1.z + ((point_2.z - point_1.z) * percentage)
    return point


def linear_reference_point_on_line(
    point_1: PointProtocol, point_2: PointProtocol, point_to_project: PointProtocol
) -> MeasurePoint:
    """Get 2d or 3d point between 2 points.

    :param point_1: shapely.geometry.Point or shapelyM.MeasurePoint
    :param point_2: shapely.geometry.Point or shapelyM.MeasurePoint
    :param point_to_project: shapely.geometry.Point or shapelyM.MeasurePoint

    """

    if point_1.z is not None and point_2.z is not None and point_to_project.z is not None:
        point_on_line_2d = project_point_on_line(point_1, point_2, point_to_project)
        point_on_line_2d = _correct_overshoot(point_1, point_2, point_on_line_2d)
        point_on_line_3d = _set_z_on_percentage(point_1, point_2, point_on_line_2d)
        return point_on_line_3d

    else:
        point_on_line_2d = project_point_on_line(point_1, point_2, point_to_project)
        point_on_line_2d = _correct_overshoot(point_1, point_2, point_on_line_2d)
        return point_on_line_2d
