from __future__ import annotations

from typing import List

from shapely.geometry import LineString, Point

from shapelyM.helpers import point_on_line, is_between
from shapelyM.measurePoint import MeasurePoint
from shapelyM.projection import LineProjection


class LineStringMeasure:
    def __init__(self, coordinates: List[List[float]]):
        self.shapely: LineString = LineString(coordinates)
        self._line_coordinates_raw: List[List[float]] = coordinates
        self.line_measure_points: List[MeasurePoint] = self._calculate_length(coordinates)
        self.length_3d: float = self._get_length()
        self.length_2d: float = self._get_length(force_2d=True)

    def _get_length(self, force_2d: bool = False) -> float:
        if force_2d:
            return self._calculate_length(self._line_coordinates_raw, force_2d=True)[-1].m
        return self.line_measure_points[-1].m

    @staticmethod
    def _calculate_length(coordinates, force_2d: bool = False) -> List[MeasurePoint]:
        _length = 0
        response = []
        for idx, item in enumerate(coordinates):
            line_point = MeasurePoint(*item)

            if idx != 0:
                line_point_min_1 = MeasurePoint(*coordinates[idx - 1])
                if force_2d:
                    _length = _length + line_point.distance(line_point_min_1, force_2d=True)
                else:
                    _length = _length + line_point.distance(line_point_min_1)
            response.append(MeasurePoint(*line_point.coordinate_list(), m=_length))
        return response

    def project(self, point: MeasurePoint) -> LineProjection:
        distance_idx = [[point.distance(line_point, force_2d=True), idx, line_point] for idx, line_point in enumerate(self.line_measure_points)]
        distance_idx.sort(key=lambda x: x[0])
        idx = distance_idx[0][1]

        if distance_idx[0][0] == distance_idx[1][0]:
            l_p1 = self.line_measure_points[distance_idx[0][1]]
            l_p2 = self.line_measure_points[distance_idx[1][1]]
            return LineProjection(l_p1, l_p2, point)

        else:
            closest_point = self.line_measure_points[idx]

            previous_point = None
            if idx != 0:
                previous_point = self.line_measure_points[idx-1]

            next_point = None
            if idx + 1 != len(self.line_measure_points):
                next_point = self.line_measure_points[idx+1]

            if not previous_point:
                projected_on_line = point_on_line(closest_point, next_point, point)
                projected_on_line_point = MeasurePoint(*projected_on_line)

                if is_between(self.line_measure_points[0], self.line_measure_points[1], projected_on_line_point):
                    return LineProjection(closest_point, next_point, point)

                return LineProjection(self.line_measure_points[0], self.line_measure_points[1], point, point_on_line_over_rule=self.line_measure_points[0])

            elif not next_point:
                return LineProjection(previous_point, closest_point, point, point_on_line_over_rule=self.line_measure_points[-1])

            else:
                projected_on_line = point_on_line(previous_point, closest_point, point)
                projected_on_line_point = MeasurePoint(*projected_on_line)
                on_previous = is_between(previous_point, closest_point, projected_on_line_point)
                next_projected = point_on_line(closest_point, next_point, point)
                next_projected_point = MeasurePoint(*next_projected)
                on_next = is_between(closest_point, next_point, next_projected_point)

                if on_previous and not on_next:
                    return LineProjection(previous_point, closest_point, point)

                elif on_next and not on_previous:
                    return LineProjection(closest_point, next_projected_point, point)

                else:
                    # on both should be closest and next
                    return LineProjection(closest_point, next_point, point)

