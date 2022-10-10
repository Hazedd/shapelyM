from __future__ import annotations

import numpy as np
from typing import Union, cast
from shapely.geometry import Point

from shapelyM.helpers import check_point_between_points
from shapelyM.measurePoint import MeasurePoint


def linear_reference_point_on_line(a: MeasurePoint, b: MeasurePoint, p: MeasurePoint):
    if a.z is not None and b.z is not None and p.z is not None:
        point_on_line_2d = project_point_on_line(
            MeasurePoint(a.x, a.y), MeasurePoint(b.x, b.y), MeasurePoint(p.x, p.y)
        )
        # check if on line part
        if not check_point_between_points(a, b, MeasurePoint(*point_on_line_2d)):
            point_on_line_2d = [b.x, b.y]

        point = MeasurePoint(point_on_line_2d[0], point_on_line_2d[1])
        start_distance = point.distance(a, force_2d=True)
        end_distance = a.distance(b, force_2d=True)
        try:
            percentage = start_distance / end_distance
        except ZeroDivisionError:
            percentage = 0

        point.z = a.z + ((b.z - a.z) * percentage)
        return project_point_on_line(a, b, point)
    else:
        point_on_line_2d = project_point_on_line(a, b, p)
        # check if on line part
        if not check_point_between_points(a, b, MeasurePoint(*point_on_line_2d)):
            point_on_line_2d = [b.x, b.y]

        return point_on_line_2d


def project_point_on_line(
    point_1: Union[Point, MeasurePoint],
    point_2: Union[Point, MeasurePoint],
    point_to_project: Union[Point, MeasurePoint],
    belong_to_segment: bool = False,
) -> np.ndarray:
    """A.....

    Todo:
     - make minimal typehint dataclass for input and output

    :param point_1: shapely.geometry.Point or shapelyM.MeasurePoint
    :param point_2: shapely.geometry.Point or shapelyM.MeasurePoint
    :param point_to_project: shapely.geometry.Point or shapelyM.MeasurePoint
    :param belong_to_segment: returns the closest vertices

    :return: Point as a np.ndarray
    """
    if point_1.x == point_2.x and point_1.y == point_2.y:
        return np.array([point_1.x, point_1.y, point_1.z])

    a_ = np.array([float(point_1.x), float(point_1.y)])
    b_ = np.array([float(point_2.x), float(point_2.y)])
    p_ = np.array([float(point_to_project.x), float(point_to_project.y)])

    point_1 = [point_1.x, point_1.y, point_1.z]
    point_2 = [point_2.x, point_2.y, point_2.z]

    ap = p_ - a_
    ab = b_ - a_
    if not belong_to_segment:
        point_2d = a_ + np.dot(ap, ab) / np.dot(ab, ab) * ab
        if point_1[2] is not None and point_2[2] is not None:
            z = get_z_between_points(point_1, point_2, point_2d)
            point_3d = np.append(point_2d, z)
            return cast(np.ndarray, point_3d)
        return cast(np.ndarray, point_2d)
    else:
        t = np.dot(ap, ab) / np.dot(ab, ab)
        t = max(0, min(1, t))
        response = a_ + t * ab
        return cast(np.ndarray, response)


def get_z_between_points(point_1, point_2, point):
    x1 = point_1[0]
    x2 = point_2[0]
    y1 = point_1[1]
    y2 = point_2[1]
    z1 = point_1[2]
    z2 = point_2[2]

    x = point[0]
    y = point[1]

    if (x2 - x1) != 0:
        z = ((x - x1) / (x2 - x1)) * (z2 - z1) + z1
    else:
        z = ((y - y1) / (y2 - y1)) * (z2 - z1) + z1

    return z


def get_y_between_points(point_1, point_2, x):
    x1 = point_1[0]
    x2 = point_2[0]
    y1 = point_1[1]
    y2 = point_2[1]

    if (x2 - x1) != 0:
        y = ((x - x1) / (x2 - x1)) * (y2 - y1) + y1
    else:
        y = min(y1, y2) + max(y1, y2) / 2

    return y
