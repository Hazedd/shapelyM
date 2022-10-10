from __future__ import annotations

import math
from enum import Enum
from typing import Union

import numpy as np
from shapely.geometry import LineString, Point

from shapelyM.measurePoint import MeasurePoint


def check_point_between_points(
    point_1: Union[Point, MeasurePoint],
    point_2: Union[Point, MeasurePoint],
    point_to_check: Union[Point, MeasurePoint],
) -> bool:
    """Methode to check if a 2d point is between two other 2d points.

    Todo:
     - make 2 dimensional check
     - make minimal typehint dataclass

    :param point_1: shapely.geometry.Point or shapelyM.MeasurePoint
    :param point_2: shapely.geometry.Point or shapelyM.MeasurePoint
    :param point_to_check: shapely.geometry.Point or shapelyM.MeasurePoint

    :return: True if between points, False if not
    """
    cross_product = (point_to_check.y - point_1.y) * (point_2.x - point_1.x) - (
        point_to_check.x - point_1.x
    ) * (point_2.y - point_1.y)

    # compare versus epsilon for floating point values, or != 0 if using integers
    if abs(cross_product) > 0.0000001:  # sys.float_info.epsilon:
        return False

    dot_product = (point_to_check.x - point_1.x) * (point_2.x - point_1.x) + (
        point_to_check.y - point_1.y
    ) * (point_2.y - point_1.y)
    if dot_product < 0:
        return False

    squared_length_ba = (point_2.x - point_1.x) * (point_2.x - point_1.x) + (point_2.y - point_1.y) * (
        point_2.y - point_1.y
    )
    if dot_product > squared_length_ba:
        return False

    return True


def get_azimuth_from_points(point1: Union[Point, MeasurePoint], point2: Union[Point, MeasurePoint]) -> float:
    """Calculates the azimuth (rotation, north == 0) by two 2d points.

    Todo:
     - make minimal typehint dataclass

    :param point1: shapely.geometry.Point or shapelyM.MeasurePoint
    :param point2: shapely.geometry.Point or shapelyM.MeasurePoint

    :return: azimuth value as a float
    """
    angle = np.arctan2(point2.x - point1.x, point2.y - point1.y)
    return float(np.degrees(angle)) if angle >= 0 else float(np.degrees(angle) + 360)


class LeftRightOnLineEnum(str, Enum):
    """Enumeration to determinate if a Point is on left or right of a line."""

    left = "Left"
    right = "Right"
    on_vector = "On"


def determinate_left_right_on_line(
    point_to_check: Point,
    azimuth: float,
    shapely_line: LineString,
    projection_distance: float = 0.2,
) -> LeftRightOnLineEnum:
    """Check and return left, right or on given a shapely linestring, point and rotation.

    :param point_to_check: point to check as shapely.geometry.Point
    :param azimuth: rotation from north as a float
    :param shapely_line: line geometry as a shapely.geometry.LineString
    :param projection_distance:
    :return: shapelyM.LeftRightOnLineEnum
    """
    while azimuth < -0:
        azimuth = +360

    angle = 90 - azimuth
    angle_rad = math.radians(angle)
    end_point_projected_on_azimuth = Point(
        point_to_check.x + projection_distance * math.cos(angle_rad),
        point_to_check.y + projection_distance * math.sin(angle_rad),
    )

    # CAN NOT HANDLE POINTS IN FRONT OF LINE, WILL RETURN 0.0 THAT WILL RESULT IN ON VECTOR

    # if same, adjust point measure -0.00000000
    object_measure = shapely_line.project(point_to_check)
    projected_measure = shapely_line.project(end_point_projected_on_azimuth)
    if object_measure == projected_measure:
        object_measure = object_measure - 0.00001
    object_point_on_line = shapely_line.interpolate(object_measure)
    projected_point_on_line = shapely_line.interpolate(projected_measure)

    _value = np.sign(
        (object_point_on_line.x - projected_point_on_line.x) * (point_to_check.y - projected_point_on_line.y)
        - (object_point_on_line.y - projected_point_on_line.y)
        * (point_to_check.x - projected_point_on_line.x)
    )

    distance = point_to_check.distance(shapely_line)

    if distance < projection_distance or _value == 0:
        return LeftRightOnLineEnum.on_vector
    elif _value < 0:
        return LeftRightOnLineEnum.left
    elif _value > 0:
        return LeftRightOnLineEnum.right

    raise ValueError
