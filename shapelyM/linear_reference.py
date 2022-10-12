from __future__ import annotations

from shapelyM.helpers import check_point_between_points, project_point_on_line, PointProtocol
from shapelyM.measurePoint import MeasurePoint


def linear_reference_point_on_line(
    point_1: PointProtocol, point_2: PointProtocol, point_to_project: PointProtocol
):
    """Get 2d or 3d point between 2 points.

    :param point_1: shapely.geometry.Point or shapelyM.MeasurePoint
    :param point_2: shapely.geometry.Point or shapelyM.MeasurePoint
    :param point_to_project: shapely.geometry.Point or shapelyM.MeasurePoint

    """
    def _project_3d():
        point_on_line_2d = project_point_on_line(
            MeasurePoint(point_1.x, point_1.y),
            MeasurePoint(point_2.x, point_2.y),
            MeasurePoint(point_to_project.x, point_to_project.y),
        )
        # check if on line part
        if not check_point_between_points(point_1, point_2, MeasurePoint(*point_on_line_2d)):
            point_on_line_2d = [point_2.x, point_2.y]

        point = MeasurePoint(point_on_line_2d[0], point_on_line_2d[1])
        start_distance = point.distance(point_1, force_2d=True)
        end_distance = point_1.distance(point_2, force_2d=True)
        try:
            percentage = start_distance / end_distance
        except ZeroDivisionError:
            percentage = 0

        point.z = point_1.z + ((point_2.z - point_1.z) * percentage)
        return project_point_on_line(point_1, point_2, point)


    def _project_2d():
        point_on_line_2d = project_point_on_line(point_1, point_2, point_to_project)
        # check if on line part
        if not check_point_between_points(point_1, point_2, MeasurePoint(*point_on_line_2d)):
            point_on_line_2d = [point_2.x, point_2.y]

        return point_on_line_2d

    
    if point_1.z is not None and point_2.z is not None and point_to_project.z is not None:
        return _project_3d()

    else:
        return _project_2d()
