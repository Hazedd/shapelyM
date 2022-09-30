from __future__ import annotations

from linear_reference import linear_reference_point_on_line
from lineString import MeasurePoint

from shapely.geometry import Point, LineString

DEBUG = False
if DEBUG:
    from debug.autocad import AutocadService
    acad = AutocadService()


class LineProjection:
    def __init__(self, line_point_1, line_point_2, point, point_on_line_over_rule=None):
        self.point = point
        self.point_on_line = MeasurePoint(*linear_reference_point_on_line(line_point_1, line_point_2, point))
        self.distance_to_line = self.point.distance(self.point_on_line)

        if point_on_line_over_rule is not None:
            self.point_on_line = point_on_line_over_rule
            self.distance_along_line = point_on_line_over_rule.m
        else:
            self.distance_along_line = line_point_1.m + line_point_1.distance(self.point_on_line)

        if DEBUG:
            if point.z is not None:
                acad.DrawShapelyObject(Point(point.x, point.y, point.z))
            else:
                acad.DrawShapelyObject(Point(point.x, point.y))
            if line_point_1.z is not None and line_point_2.z is not None:
                acad.DrawShapelyObject(LineString([
                    [line_point_1.x, line_point_1.y, line_point_1.z],
                    [line_point_2.x, line_point_2.y, line_point_2.z]
                ]))
            else:
                acad.DrawShapelyObject(LineString([
                    [line_point_1.x, line_point_1.y],
                    [line_point_2.x, line_point_2.y]
                ]))

            if self.point_on_line.z is not None:
                acad.DrawShapelyObject(Point(self.point_on_line.x, self.point_on_line.y, self.point_on_line.z))
            else:
                acad.DrawShapelyObject(Point(self.point_on_line.x, self.point_on_line.y))

            if self.point_on_line.z is not None and point.z is not None:
                acad.DrawShapelyObject(LineString([
                    [self.point_on_line.x, self.point_on_line.y, self.point_on_line.z],
                    [point.x, point.y, point.z]
                ]))
            else:
                acad.DrawShapelyObject(LineString([
                    [self.point_on_line.x, self.point_on_line.y],
                    [point.x, point.y]
                ]))
