from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Union

from shapely.geometry import LineString, Point

from shapelyM.helpers import (
    MinimalPoint,
    check_point_between_points,
    get_z_between_points,
    project_point_on_line,
)
from shapelyM.linear_reference import get_line_projection
from shapelyM.measurePoint import MeasurePoint


@dataclass
class DistancePoint:
    index: str
    measurePoint: MeasurePoint
    distance: float


@dataclass
class DistancePoints:
    values: List[DistancePoint]

    def sorted_on_distance(self) -> List[DistancePoint]:
        self.values.sort(key=lambda x: x.distance)
        return self.values


class MeasureLineString:
    def __init__(self, coordinates: List[List[float]]):
        """First implementation of main linestring object.

        Todo:
          - major refactor / redesign
          - support scaled measure lines
          - cut linestring by measure and functional direction
          - get profile by from measures and functional direction

        """
        self._line_coordinates_raw: List[List[float]] = coordinates
        if len(coordinates[0]) > 3:
            # todo: add parameter to see it's a m linestring
            self.shapely: LineString = LineString([item[:3] for item in coordinates])
        else:
            self.shapely: LineString = LineString(coordinates)

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
                if line_point.m is None:
                    if force_2d:
                        _length = _length + line_point.distance(line_point_min_1, force_2d=True)
                    else:
                        _length = _length + line_point.distance(line_point_min_1)
                else:
                    _length = line_point.m
            response.append(MeasurePoint(*line_point.coordinate_list(), m=_length))
        return response

    def _get_points_sorted_on_distance(self, point: MeasurePoint) -> List[DistancePoint]:
        return DistancePoints(
            [
                DistancePoint(
                    index=idx, measurePoint=line_point, distance=point.distance(line_point, force_2d=True)
                )
                for idx, line_point in enumerate(self.line_measure_points)
            ]
        ).sorted_on_distance()

    def project(
        self, point: Union[MeasurePoint, Point], azimuth: Optional[float] = None
    ) -> get_line_projection:
        """..........

        :param point:
        :param azimuth:
        :return:
        """
        if isinstance(point, Point):
            point = MeasurePoint(*point.coords[0])

        points_sorted_on_distance = self._get_points_sorted_on_distance(point)
        closed_point_index = points_sorted_on_distance[0].index

        # exactly in the middle of 2 points
        if points_sorted_on_distance[0].distance == points_sorted_on_distance[1].distance:
            return get_line_projection(
                self.line_measure_points[points_sorted_on_distance[0].index],
                self.line_measure_points[points_sorted_on_distance[1].index],
                point,
            )

        else:
            closest_point = self.line_measure_points[closed_point_index]

            previous_point = None
            if closed_point_index != 0:
                previous_point = self.line_measure_points[closed_point_index - 1]

            next_point = None
            if closed_point_index + 1 != len(self.line_measure_points):
                next_point = self.line_measure_points[closed_point_index + 1]

            if not previous_point:
                # should be on first part of the line
                projected_on_line = project_point_on_line(
                    closest_point, self.line_measure_points[closed_point_index + 1], point
                ).coords
                projected_on_line_point = MeasurePoint(*projected_on_line)

                # return if between points
                if check_point_between_points(
                    self.line_measure_points[0],
                    self.line_measure_points[1],
                    projected_on_line_point,
                ):
                    return get_line_projection(closest_point, next_point, point)

                # else point undershoot line return first point
                return get_line_projection(
                    self.line_measure_points[0],
                    self.line_measure_points[1],
                    point,
                    point_on_line_overrule=self.line_measure_points[0],
                )

            elif not next_point:
                # end of the line or overshoot, so force last point
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

    def get_line_m(self, measure: float):
        return self._cut(self, measure)

    def get_profile(self, from_measure: float, to_measure: float):
        pre_cut = self._cut(self, from_measure)[1]
        result = self._cut(pre_cut, (to_measure - from_measure))[0]
        return result

    @staticmethod
    def _cut(line: MeasureLineString, measure: float) -> List[MeasureLineString]:

        if measure <= 0.0 or measure >= line.line_measure_points[-1].m:
            return [line]

        coords = line.line_measure_points
        for i, p in enumerate(coords):
            pd = p.m

            if pd == measure:
                return [MeasureLineString(coords[: i + 1]), MeasureLineString(coords[i:])]

            if pd > measure:
                # get total distance between points 3d
                line_segment_length = coords[i - 1].distance(coords[i])

                # get previous measure and correct measure length
                segment_measure = measure - coords[i - 1].m
                distance_along_line = segment_measure / line_segment_length

                # make 2d line
                line = LineString([coords[i - 1].coordinate_list()[:2], coords[i].coordinate_list()[:2]])

                # project
                point_along_line = line.interpolate(distance_along_line)
                point_along_line = MinimalPoint(point_along_line.x, point_along_line.y)

                # get z
                tester = MinimalPoint(point_along_line.x, point_along_line.y)
                point_along_line.z = get_z_between_points(coords[i - 1], coords[i], tester)

                # make 3d line form start
                point_list = [item.coordinate_list() for idx, item in enumerate(coords) if idx < i]
                point_list.append([point_along_line.x, point_along_line.y, point_along_line.z])
                line_1 = MeasureLineString(point_list)

                # make 3d line to end
                point_list = [[point_along_line.x, point_along_line.y, point_along_line.z]]
                points_to_end = [item.coordinate_list() for idx, item in enumerate(coords) if idx >= i]
                point_list.extend(points_to_end)
                line_2 = MeasureLineString(point_list)

                return [line_1, line_2]
