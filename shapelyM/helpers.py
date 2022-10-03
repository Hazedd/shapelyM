from __future__ import annotations

import math
from enum import Enum
from typing import Union, cast

import numpy as np
from shapely.geometry import LineString, Point

from shapelyM.measurePoint import MeasurePoint


def point_on_line(
    a: Union[MeasurePoint, Point],
    b: Union[MeasurePoint, Point],
    p: Union[MeasurePoint, Point],
    belong_to_segment: bool = False,
) -> np.ndarray:
    """......

    :param a:
    :param b:
    :param p:
    :param belong_to_segment:
    :return:
    """
    if a.x == b.x and a.y == b.y:
        return np.array([a.x, a.y, a.z])

    if a.z is not None and b.z is not None and p.z is not None:
        a_ = np.array([a.x, a.y, a.z])
        b_ = np.array([b.x, b.y, b.z])
        p_ = np.array([p.x, p.y, p.z])

    else:
        a_ = np.array([a.x, a.y])
        b_ = np.array([b.x, b.y])
        p_ = np.array([p.x, p.y])

    ap = p_ - a_
    ab = b_ - a_
    if not belong_to_segment:
        response = a_ + np.dot(ap, ab) / np.dot(ab, ab) * ab
        return cast(np.ndarray, response)
    else:
        t = np.dot(ap, ab) / np.dot(ab, ab)
        t = max(0, min(1, t))
        response = a_ + t * ab
        return cast(np.ndarray, response)


def is_between(a: MeasurePoint, b: MeasurePoint, c: MeasurePoint) -> bool:
    """.....

    # todo: make sure it handles 3d.

    :param a:
    :param b:
    :param c:
    :return:
    """
    cross_product = (c.y - a.y) * (b.x - a.x) - (c.x - a.x) * (b.y - a.y)

    # compare versus epsilon for floating point values, or != 0 if using integers
    if abs(cross_product) > 0.0000001:  # sys.float_info.epsilon:
        return False

    dot_product = (c.x - a.x) * (b.x - a.x) + (c.y - a.y) * (b.y - a.y)
    if dot_product < 0:
        return False

    squared_length_ba = (b.x - a.x) * (b.x - a.x) + (b.y - a.y) * (b.y - a.y)
    if dot_product > squared_length_ba:
        return False

    return True


def get_azimuth_from_points(point1: Point, point2: Point) -> float:
    """
    .........

    :param point1:
    :param point2:
    :return:
    """
    angle = np.arctan2(point2.x - point1.x, point2.y - point1.y)
    return float(np.degrees(angle)) if angle >= 0 else float(np.degrees(angle) + 360)


class LeftRightOnLineEnum(str, Enum):
    """......"""

    left = "Left"
    right = "Right"
    on_vector = "On"


def determinate_left_right_on_line(
    object_location: Point,
    azimuth: float,
    line_geometry: LineString,
    margin: float = 0.2,
) -> LeftRightOnLineEnum:
    """Get point left or right from a given line and rotation.

    :param object_location:
    :param azimuth:
    :param line_geometry:
    :param margin:
    :return:
    """
    projection_length = 1

    while azimuth < -0:
        azimuth = +360

    angle = 90 - azimuth
    angle_rad = math.radians(angle)
    end_point_projected_on_azimuth = Point(
        object_location.x + projection_length * math.cos(angle_rad),
        object_location.y + projection_length * math.sin(angle_rad),
    )

    object_measure = line_geometry.project(object_location)
    projected_measure = line_geometry.project(end_point_projected_on_azimuth)

    object_point_on_line = line_geometry.interpolate(object_measure)
    projected_point_on_line = line_geometry.interpolate(projected_measure)

    _value = np.sign(
        (object_point_on_line.x - projected_point_on_line.x) * (object_location.y - projected_point_on_line.y)
        - (object_point_on_line.y - projected_point_on_line.y)
        * (object_location.x - projected_point_on_line.x)
    )

    distance = object_location.distance(line_geometry)

    if distance < margin or _value == 0:
        return LeftRightOnLineEnum.on_vector
    elif _value < 0:
        return LeftRightOnLineEnum.left
    elif _value > 0:
        return LeftRightOnLineEnum.right

    raise ValueError
