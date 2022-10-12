from __future__ import annotations

import math
from typing import List

from shapely.geometry import Point

from shapelyM.helpers import MinimalPoint


class MeasurePoint:
    def __init__(self, x: float, y: float, z: float = None, m: float = None):
        """..........

        :param x:
        :param y:
        :param z:
        :param m:
        """
        self.x = float(x)
        self.y = float(y)
        self.z = z
        self.m = m
        self.shapely = Point(self.coordinate_list())

    def coordinate_list(self) -> List[float]:
        if self.z is not None:
            return [self.x, self.y, self.z]
        return [self.x, self.y]

    def distance(self, point_geometry: MinimalPoint, force_2d: bool = False) -> float:
        if self.z is not None and point_geometry.z is not None and force_2d is not True:
            return math.sqrt(
                math.pow(point_geometry.x - self.x, 2)
                + math.pow(point_geometry.y - self.y, 2)
                + math.pow(point_geometry.z - self.z, 2) * 1.0
            )
        else:
            return math.sqrt((self.x - point_geometry.x) ** 2 + (self.y - point_geometry.y) ** 2)
