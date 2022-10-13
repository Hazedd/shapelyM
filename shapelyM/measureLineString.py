from __future__ import annotations

from typing import Any, Dict, List, Optional

from shapely.geometry import LineString, Point

from shapelyM.helpers import check_point_between_points, project_point_on_line
from shapelyM.linear_reference import get_line_projection
from shapelyM.measurePoint import MeasurePoint


class MeasureLineString:
    def __init__(self, coordinates: List[List[float]]):
        """..........

        Todo:
          - major refactor
        """
        self.shapely: LineString = LineString(coordinates)
        self._line_coordinates_raw: List[List[float]] = coordinates
        self.line_measure_points: List[MeasurePoint] = self._calculate_length(coordinates)
        self.length_3d: Optional[float] = self._get_length()
        self.length_2d: Optional[float] = self._get_length(force_2d=True)

    def _get_length(self, force_2d: bool = False) -> Optional[float]:
        if force_2d:
            return self._calculate_length(self._line_coordinates_raw, force_2d=True)[-1].m
        return self.line_measure_points[-1].m

    @staticmethod
    def _calculate_length(coordinates, force_2d: bool = False) -> List[MeasurePoint]:
        _length = 0.0
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

    def _get_distance_idx_dict(self, point: MeasurePoint) -> Dict[str, List[Any]]:
        distance_idx = [
            [point.distance(line_point, force_2d=True), idx, line_point]
            for idx, line_point in enumerate(self.line_measure_points)
        ]
        distance_idx.sort(key=lambda x: x[0])
        return distance_idx

    def project(
        self, point: Optional[MeasurePoint, Point], azimuth: Optional[float] = None
    ) -> get_line_projection:
        """..........

        :param point:
        :param azimuth:
        :return:
        """
        if isinstance(point, Point):
            point = MeasurePoint(*point.coords[0])

        distance_idx = self._get_distance_idx_dict(point)
        idx = int(distance_idx[0][1])

        if distance_idx[0][0] == distance_idx[1][0]:
            l_p1 = self.line_measure_points[distance_idx[0][1]]
            l_p2 = self.line_measure_points[distance_idx[1][1]]
            # point exactly in the middle of the line
            return get_line_projection(l_p1, l_p2, point)

        else:
            closest_point = self.line_measure_points[idx]

            previous_point = None
            if idx != 0:
                previous_point = self.line_measure_points[idx - 1]

            next_point = None
            if idx + 1 != len(self.line_measure_points):
                next_point = self.line_measure_points[idx + 1]

            if not previous_point:
                projected_on_line = project_point_on_line(
                    closest_point, self.line_measure_points[idx + 1], point
                ).coords
                projected_on_line_point = MeasurePoint(*projected_on_line)

                # on first part of the line
                if check_point_between_points(
                    self.line_measure_points[0],
                    self.line_measure_points[1],
                    projected_on_line_point,
                ):
                    return get_line_projection(closest_point, next_point, point)

                # point in front of the line: undershoot
                return get_line_projection(
                    self.line_measure_points[0],
                    self.line_measure_points[1],
                    point,
                    point_on_line_overrule=self.line_measure_points[0],
                )

            elif not next_point:
                # somewhere on last part of line..
                return get_line_projection(previous_point, closest_point, point)

            else:
                # somewhere on the line
                projected_on_line = project_point_on_line(previous_point, closest_point, point).coords
                projected_on_line_point = MeasurePoint(*projected_on_line)
                on_previous = check_point_between_points(
                    previous_point, closest_point, projected_on_line_point
                )
                next_projected = project_point_on_line(closest_point, next_point, point).coords
                next_projected_point = MeasurePoint(*next_projected)
                on_next = check_point_between_points(closest_point, next_point, next_projected_point)

                if on_previous and not on_next:
                    # on segment before the closest point
                    return get_line_projection(previous_point, closest_point, point)

                elif on_next and not on_previous:
                    # on segment after the closest point
                    return get_line_projection(closest_point, next_point, point)

                else:
                    # on vertices
                    return get_line_projection(closest_point, next_point, point)
