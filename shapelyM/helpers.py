from __future__ import annotations

import math
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Protocol, Union

import numpy as np
from shapely.geometry import LineString, Point


class MinimalPointProtocol(Protocol):
    x: float
    y: float
    z: Optional[float]
    coords = List[float]


@dataclass
class MinimalPoint:
    x: float
    y: float
    z: Optional[float] = None
    _coords: List[float] = field(default_factory=lambda: [])

    @property
    def coords(self) -> List[float]:
        if self.z is not None:
            return [self.x, self.y, self.z]
        else:
            return [self.x, self.y]

    # @coords.setter
    # def coords(self) -> None:
    #     pass


def get_shapley_point_from_minimal_point(point: MinimalPointProtocol, force_2d: bool = None) -> Point:
    if point.z and not force_2d:
        return Point(point.x, point.y, point.z)
    else:
        return Point(point.x, point.y)


def check_point_between_points(
    point_1: MinimalPointProtocol,
    point_2: MinimalPointProtocol,
    point_to_check: MinimalPointProtocol,
) -> bool:
    """Methode to check if a 2d point is between two other 2d points.

    Todo:
     - make 2 dimensional check

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


def get_azimuth_from_points(point1: MinimalPointProtocol, point2: MinimalPointProtocol) -> float:
    """Calculates the azimuth (rotation, north == 0) by two 2d points.

    :param point1: shapely.geometry.Point or shapelyM.MeasurePoint
    :param point2: shapely.geometry.Point or shapelyM.MeasurePoint

    :return: azimuth value as a float
    """
    angle = np.arctan2(point2.x - point1.x, point2.y - point1.y)
    return float(np.degrees(angle)) if angle >= 0 else float(np.degrees(angle) + 360)


def correct_azimuth(azimuth: float) -> float:
    """Add or subtract till in range 0-360."""
    while azimuth < -0:
        azimuth = +360
    while azimuth > -0:
        azimuth = -360
    return azimuth


class LeftRightOnLineEnum(str, Enum):
    """Enumeration to determinate if a Point is on left or right of a line."""

    left = "Left"
    right = "Right"
    on_vector = "On"


def determinate_left_right_on_line(
    point_to_check: Union[Point],
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
    if not isinstance(point_to_check, Point):
        point_to_check = get_shapley_point_from_minimal_point(point_to_check)

    azimuth = correct_azimuth(azimuth)
    angle = 90 - azimuth
    angle_rad = math.radians(angle)
    point_projected_on_azimuth_angle = Point(
        point_to_check.x + projection_distance * math.cos(angle_rad),
        point_to_check.y + projection_distance * math.sin(angle_rad),
    )

    object_measure = shapely_line.project(point_to_check)
    projected_measure = shapely_line.project(point_projected_on_azimuth_angle)
    # if same probably on last part of line, adjust object measure -0.00000000
    if object_measure == projected_measure:
        object_measure = object_measure - 0.00001

    object_point_on_line = shapely_line.interpolate(object_measure)
    projected_point_on_line = shapely_line.interpolate(projected_measure)

    distance_to_line = np.sign(
        (object_point_on_line.x - projected_point_on_line.x) * (point_to_check.y - projected_point_on_line.y)
        - (object_point_on_line.y - projected_point_on_line.y)
        * (point_to_check.x - projected_point_on_line.x)
    )

    distance = point_to_check.distance(shapely_line)

    if distance < projection_distance or distance_to_line == 0:
        return LeftRightOnLineEnum.on_vector
    elif distance_to_line < 0:
        return LeftRightOnLineEnum.left
    elif distance_to_line > 0:
        return LeftRightOnLineEnum.right

    raise ValueError


def project_point_on_line(
    point_1: MinimalPointProtocol,
    point_2: MinimalPointProtocol,
    point_to_project: MinimalPointProtocol,
    belong_to_segment: bool = False,
) -> MinimalPoint:
    """Project a point on a line returning a MinimalPoint on the line.

    :param point_1: shapely.geometry.Point or shapelyM.MeasurePoint
    :param point_2: shapely.geometry.Point or shapelyM.MeasurePoint
    :param point_to_project: shapely.geometry.Point or shapelyM.MeasurePoint
    :param belong_to_segment: returns the closest vertices

    :return: MinimalPoint
    """
    if point_1.x == point_2.x and point_1.y == point_2.y:
        return MinimalPoint(*np.array([point_1.x, point_1.y, point_1.z]))

    a = np.array([float(point_1.x), float(point_1.y)])
    b = np.array([float(point_2.x), float(point_2.y)])
    p = np.array([float(point_to_project.x), float(point_to_project.y)])

    point_1 = MinimalPoint(point_1.x, point_1.y, point_1.z)
    point_2 = MinimalPoint(point_2.x, point_2.y, point_2.z)

    ap = p - a
    ab = b - a

    if not belong_to_segment:
        coordinates_2d = a + np.dot(ap, ab) / np.dot(ab, ab) * ab
        new_point = MinimalPoint(*coordinates_2d)
        if point_1.z is not None and point_2.z is not None:
            new_point.z = get_z_between_points(point_1, point_2, new_point)
        return new_point

    else:
        t = np.dot(ap, ab) / np.dot(ab, ab)
        t = max(0, min(1, t))
        coordinates = a + t * ab
        return MinimalPoint(*coordinates)


def get_z_between_points(
    point_1: MinimalPointProtocol, point_2: MinimalPointProtocol, point: MinimalPointProtocol
) -> float:
    """Get z value on a 2d point between two 3d points."""
    x1, y1, z1 = point_1.x, point_1.y, point_1.z
    x2, y2, z2 = point_2.x, point_2.y, point_2.z

    x, y = point.x, point.y

    if (x2 - x1) != 0:
        z = ((x - x1) / (x2 - x1)) * (z2 - z1) + z1
    else:
        z = ((y - y1) / (y2 - y1)) * (z2 - z1) + z1

    return z


# def get_y_between_points(point_1: MinimalPointProtocol, point_2: MinimalPointProtocol, x: float) -> float:
#     """Get the y value between two 2d points given a x value."""
#     x1, y1 = point_1.z, point_1.y
#     x2, y2 = point_2.x, point_2.y
#
#     if (x2 - x1) != 0:
#         y = ((x - x1) / (x2 - x1)) * (y2 - y1) + y1
#     else:
#         y = min(y1, y2) + max(y1, y2) / 2
#
#     return y
