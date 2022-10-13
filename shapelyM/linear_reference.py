from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from shapely.geometry import LineString, Point

from shapelyM.helpers import (
    LeftRightOnLineEnum,
    MinimalPoint,
    MinimalPointProtocol,
    check_point_between_points,
    determinate_left_right_on_line,
    get_azimuth_from_points,
    get_z_between_points,
    project_point_on_line,
)
from shapelyM.measurePoint import MeasurePoint


@dataclass
class LineProjection:
    """Xxxx.

    Xxxxxxx.

    Args:
        name (type): xxx.

    """

    point: MeasurePoint
    azimuth: float
    side_of_line: LeftRightOnLineEnum
    point_on_line: MeasurePoint
    distance_to_line_2d: float
    distance_to_line_3d: float
    distance_along_line: float


def _correct_overshoot(
    point_1: MinimalPointProtocol, point_2: MinimalPointProtocol, point_on_line_2d: MinimalPointProtocol
) -> MinimalPoint:
    """
    If not between the points, we assume it overshoots, and sets last point as point on line.

    :param point_1: shapely.geometry.Point or shapelyM.MeasurePoint
    :param point_2: shapely.geometry.Point or shapelyM.MeasurePoint
    :param point_to_project: shapely.geometry.Point or shapelyM.MeasurePoint
    :returns
    """
    #
    if not check_point_between_points(point_1, point_2, point_on_line_2d):
        point_on_line_2d = MinimalPoint(point_2.x, point_2.y)
    return point_on_line_2d


def _get_3d_point_on_line(
    point_1: MinimalPointProtocol, point_2: MinimalPointProtocol, point_to_project: MinimalPointProtocol
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


def get_line_projection(
    line_point_1: MeasurePoint,
    line_point_2: MeasurePoint,
    point: MeasurePoint,
    point_on_line_overrule: Optional[MeasurePoint] = None,
    azimuth: Optional[float] = None,
    debug: bool = False,
) -> LineProjection:
    """.........

    :param line_point_1:
    :param line_point_2:
    :param point:
    :param point_on_line_overrule:
    :param azimuth:
    :param debug:

    """
    point_on_line = _get_3d_point_on_line(line_point_1, line_point_2, point)
    distance_to_line_2d = point.distance(point_on_line, force_2d=True)
    distance_to_line_3d = point.distance(point_on_line)

    if point_on_line_overrule is not None:
        point_on_line = point_on_line_overrule
        distance_along_line = point_on_line_overrule.m
    else:
        point_on_line = point_on_line
        distance_along_line = line_point_1.m + line_point_1.distance(point_on_line)

    point_on_line.m = distance_along_line

    if not azimuth:
        azimuth = get_azimuth_from_points(line_point_1, line_point_2)

    side_of_line = determinate_left_right_on_line(
        Point([point.x, point.y]),
        azimuth,
        LineString([[line_point_1.x, line_point_1.y], [line_point_2.x, line_point_2.y]]),
    )

    result = LineProjection(
        point=point,
        azimuth=azimuth,
        side_of_line=side_of_line,
        point_on_line=point_on_line,
        distance_to_line_2d=distance_to_line_2d,
        distance_to_line_3d=distance_to_line_3d,
        distance_along_line=distance_along_line,
    )

    if debug:
        draw_projection_in_autocad(result)
    return result


def draw_projection_in_autocad(line_projection: LineProjection):
    from debug.autocad import AutocadService

    acad = AutocadService()
    acad.DrawShapelyObject(line_projection.point.shapely)
    acad.DrawText(f"{line_projection.side_of_line.value}", line_projection.point.shapely)
    acad.DrawShapelyObject(line_projection.point_on_line.shapely)
    acad.DrawShapelyObject(
        LineString(
            [
                line_projection.point_on_line.shapely,
                line_projection.point.shapely,
            ]
        )
    )
