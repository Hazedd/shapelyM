from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from shapely.geometry import LineString, Point

from shapelyM.helpers import (
    LeftRightOnLineEnum,
    determinate_left_right_on_line,
    get_azimuth_from_points,
)
from shapelyM.linear_reference import linear_reference_point_on_line
from shapelyM.measurePoint import MeasurePoint

DEBUG = False
if DEBUG:  # pragma: no cover
    from debug.autocad import AutocadService

    acad = AutocadService()


@dataclass
class LineProjectionNew:
    point: MeasurePoint
    point_on_line: MeasurePoint
    distance_to_line_2d: float
    distance_along_line: float
    azimuth: float
    side_of_line: LeftRightOnLineEnum


class GetLineProjection:
    def __init__(
        self,
        line_point_1: MeasurePoint,
        line_point_2: MeasurePoint,
        point: MeasurePoint,
        point_on_line_overrule: Optional[MeasurePoint] = None,
        azimuth: Optional[float] = None,
    ):
        """.........

        Todo:
          - make dataclass factory!
          - refactor

        :param line_point_1:
        :param line_point_2:
        :param point:
        :param point_on_line_overrule:
        :param azimuth:
        """
        self.point = point
        self.point_on_line = linear_reference_point_on_line(line_point_1, line_point_2, point)
        self.distance_to_line = self.point.distance(self.point_on_line)
        self.distance_to_line_2d = self.point.distance(self.point_on_line, force_2d=True)
        if point_on_line_overrule is not None:
            self.point_on_line = point_on_line_overrule
            self.distance_along_line = point_on_line_overrule.m
        else:
            self.point_on_line = self.point_on_line
            self.distance_along_line = line_point_1.m + line_point_1.distance(self.point_on_line)

        self.point_on_line.m = self.distance_along_line

        if not azimuth:
            azimuth = get_azimuth_from_points(line_point_1, line_point_2)

        # check if point on last vector of line then
        self.side_of_line = determinate_left_right_on_line(
            Point([self.point.x, self.point.y]),
            azimuth,
            LineString([[line_point_1.x, line_point_1.y], [line_point_2.x, line_point_2.y]]),
        ).value

        if DEBUG:  # pragma: no cover
            # draw input point
            if point.z is not None:
                acad.DrawShapelyObject(Point(point.x, point.y, point.z))
            else:
                acad.DrawShapelyObject(Point(point.x, point.y))
            acad.DrawText(f"{self.side_of_line}", Point(point.x, point.y))

            # draw line
            if line_point_1.z is not None and line_point_2.z is not None:
                # acad.DrawText(f"start", Point(line_point_1.x, line_point_1.y))
                acad.DrawShapelyObject(
                    LineString(
                        [
                            [line_point_1.x, line_point_1.y, line_point_1.z],
                            [line_point_2.x, line_point_2.y, line_point_2.z],
                        ]
                    )
                )
            else:
                acad.DrawShapelyObject(
                    LineString([[line_point_1.x, line_point_1.y], [line_point_2.x, line_point_2.y]])
                )

            # draw point on line
            if self.point_on_line.z is not None:
                acad.DrawShapelyObject(
                    Point(self.point_on_line.x, self.point_on_line.y, self.point_on_line.z)
                )
            else:
                acad.DrawShapelyObject(Point(self.point_on_line.x, self.point_on_line.y))

            # draw point to line
            if self.point_on_line.z is not None and point.z is not None:
                acad.DrawShapelyObject(
                    LineString(
                        [
                            [self.point_on_line.x, self.point_on_line.y, self.point_on_line.z],
                            [point.x, point.y, point.z],
                        ]
                    )
                )
            else:
                acad.DrawShapelyObject(
                    LineString([[self.point_on_line.x, self.point_on_line.y], [point.x, point.y]])
                )
