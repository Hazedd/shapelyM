import math

from enum import Enum
from shapely.geometry import Point, LineString


class LeftRightOnLineEnum(str, Enum):
    left = "Left"
    right = "Right"
    on_vector = "On vector"


def determinate_point_left_right_or_on_line(
    object_location: Point,
    azimuth: float,
    line__geometry: LineString,
    margin: float = 0.2,
) -> LeftRightOnLineEnum:
    """Get point left or right from a given line and rotation.

    TODO: add test make docstrings
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

    object_measure = line__geometry.project(object_location)
    projected_measure = line__geometry.project(end_point_projected_on_azimuth)

    object_point_on_line = line__geometry.interpolate(object_measure)
    projected_point_on_line = line__geometry.interpolate(projected_measure)

    _value = np.sign(
        (object_point_on_line.x - projected_point_on_line.x)
        * (object_location.y - projected_point_on_line.y)
        - (object_point_on_line.y - projected_point_on_line.y)
        * (object_location.x - projected_point_on_line.x)
    )

    distance = object_location.distance(line__geometry)

    if distance < margin or _value == 0:
        return LeftRightOnLineEnum.on_vector
    elif _value > 0:
        return LeftRightOnLineEnum.left
    elif _value < 0:
        return LeftRightOnLineEnum.right

    raise ValueError
