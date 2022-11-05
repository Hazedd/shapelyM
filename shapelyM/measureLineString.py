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
from shapelyM.linear_reference import LineProjection, get_line_projection
from shapelyM.measurePoint import MeasurePoint

# from shapelyM.debug.autocad import AutocadService
# acad = AutocadService()


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


# todo:
#  - add has_z()
#  - make dataclass, make frozen


class MeasureLineString:
    def __init__(self, coordinates: List[List[float]], m_given: bool = False):
        self._line_coordinates_raw: List[List[float]] = coordinates
        self.m_given: bool = m_given
        self.shapely: LineString = LineString(self._get_xyz_from_coordinates(coordinates))
        self.line_measure_points: List[MeasurePoint] = self._measure_points_list_factory(coordinates)
        coordinates_xyz = self._get_xyz_from_coordinates(coordinates)
        if len(coordinates_xyz[0]) == 3:
            self.length_3d: float = self._get_length_by_geometry(coordinates_xyz)
        else:
            self.length_3d: Optional[float] = None

        self.length_2d: float = self._get_length_by_geometry(coordinates_xyz, force_2d=True)
        self.length_measure: float = self.line_measure_points[-1].m

    def coordinate_list(self):
        return [[item.x, item.y, item.z] for item in self.line_measure_points]

    def _get_xyz_from_coordinates(self, coordinates):
        if self.m_given and len(coordinates[0]) == 4 and coordinates[0][2] is None:
            return [item[:2] for item in coordinates]
        elif self.m_given and len(coordinates[0]) > 3:
            return [item[:3] for item in coordinates]
        elif self.m_given and len(coordinates[0]) > 2:
            return [item[:2] for item in coordinates]
        elif self.m_given and len(coordinates[0]) <= 2:
            raise ValueError("bad coordinates for measure line")
        else:
            return coordinates

    @staticmethod
    def _get_length_by_geometry(coordinates, force_2d: bool = False) -> List[MeasurePoint]:
        # todo: move to helpers
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
                line_point.m = _length
            else:
                line_point.m = 0
            response.append(line_point)
        return response[-1].m

    def _measure_points_list_factory(self, coordinates, force_2d: bool = False) -> List[MeasurePoint]:
        _length = 0.0
        response = []

        for idx, item in enumerate(coordinates):
            if self.m_given and len(item) == 3:
                line_point = MeasurePoint(*item[:2])
                line_point.m = item[2]
            elif self.m_given and len(item) == 4:
                line_point = MeasurePoint(*item[:3])
                line_point.m = item[3]
            else:
                line_point = MeasurePoint(*item)

            if idx != 0:
                line_point_min_1 = MeasurePoint(*coordinates[idx - 1])
                if line_point.m is None:
                    if force_2d:
                        _length = _length + line_point.distance(line_point_min_1, force_2d=True)
                    else:
                        _length = _length + line_point.distance(line_point_min_1)
                    line_point.m = _length
                else:
                    _length = line_point.m
            else:
                if line_point.m is None:
                    line_point.m = 0
            response.append(line_point)
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

    def project(self, point: Union[MeasurePoint, Point], azimuth: Optional[float] = None) -> LineProjection:
        """Returns a linear reference object given a point and an optional rotation.

        Todo:
          - return functional direction.
          - remove MeasurePoint, make sure convert outside object...

        :param point: MinimalPoint or shapely.Point
        :param azimuth: rotations as a float (seen from north to the right).
        :return: LineProjection
        """
        if self.m_given is True:
            raise NotImplementedError

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

    @staticmethod
    def _cut(line_to_cut: LineString, measure: float) -> List[MeasureLineString]:
        if measure <= 0.0:
            return [None, line_to_cut]
        elif measure >= line_to_cut.line_measure_points[-1].m:
            return [line_to_cut, None]

        coords = line_to_cut.line_measure_points
        for i, p in enumerate(coords):
            pd = p.m

            if pd == measure:
                return [
                    MeasureLineString([item.coordinate_list() for item in coords[: i + 1]]),
                    MeasureLineString([item.coordinate_list() for item in coords[i:]]),
                ]

            if pd > measure:

                # leftover measure on line segment
                if i == 0:
                    left_over_measure = measure
                else:
                    left_over_measure = measure - coords[i - 1].m

                # percentage leftover measure
                measure_length = coords[i].m - coords[i - 1].m
                percentage = left_over_measure / measure_length

                # true measure == segment length * percentage leftover
                segment_length = coords[i - 1].distance(coords[i])
                true_measure = segment_length * percentage

                # interpolate line
                line = LineString([coords[i - 1].coordinate_list()[:2], coords[i].coordinate_list()[:2]])
                point_along_line = line.interpolate(true_measure)

                # acad.DrawShapelyObject(point_along_line)

                point_along_line = MinimalPoint(point_along_line.x, point_along_line.y)
                try:
                    point_along_line.z = get_z_between_points(
                        coords[i - 1], coords[i], MinimalPoint(point_along_line.x, point_along_line.y)
                    )
                except Exception as e:
                    print(e)
                    point_along_line.z = None

                # make (3d) line form start
                point_list = [[item.x, item.y, item.z, item.m] for idx, item in enumerate(coords) if idx < i]
                if point_along_line.z is not None:
                    point_list.append([point_along_line.x, point_along_line.y, point_along_line.z, measure])
                else:
                    point_list.append([point_along_line.x, point_along_line.y, None, measure])

                # todo: make m values work
                line_1 = MeasureLineString(point_list, m_given=True)

                # make (3d) line to end
                if point_along_line.z is not None:
                    point_list = [[point_along_line.x, point_along_line.y, point_along_line.z, measure]]
                else:
                    point_list = [[point_along_line.x, point_along_line.y, None, measure]]
                points_to_end = [
                    [item.x, item.y, item.z, item.m] for idx, item in enumerate(coords) if idx >= i
                ]
                point_list.extend(points_to_end)

                # todo: make m values work
                line_2 = MeasureLineString(point_list, m_given=True)

                return [line_1, line_2]

    def cut(self, measure: float) -> List[MeasureLineString]:
        """Cut on a given measure returns both parts.

        :param: measure: line cut measure as a float.
        :return: List[MeasureLineString] where 1st is first part, 2th end part
        """
        return self._cut(self, measure)

    def cut_profile(self, from_measure: float, to_measure: float) -> MeasureLineString:
        """Cut on a given from and to measure returns the cut profile.

        :param: from_measure: line cut from measure as a float.
        :param: to_measure: line cut to measure as a float.
        :return: a MeasureLineString of the profile
        """
        if from_measure >= to_measure:
            raise ValueError("from_measure should be lower then to_measure.")

        pre_cut = self._cut(self, from_measure)[1]
        result = self._cut(pre_cut, to_measure)[0]
        return result
