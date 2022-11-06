from __future__ import annotations

from shapely.geometry import Point

from shapelyM.measureLineString import CutProfileStatus, MeasureLineString

# import json


# todo: split below to fixtures and smaller test cases in test class


def test_2d_line_cut_and_profile():
    # minimal edge case 3 as offset, same level line segments only on y offset
    line_data = [[3, 0], [3, 10], [3, 20], [3, 30]]
    line = MeasureLineString(line_data)
    assert line.m_given is False

    for idx, coordinate in enumerate(line_data):
        assert line.line_measure_points[idx].coordinate_list() == coordinate
        assert line.line_measure_points[idx].m == coordinate[1]

    assert line.length_2d == 30
    assert line.shapely.length == line.length_2d
    assert line.length_3d is None
    assert line.end_measure == 30

    # minimal project test, use center of lin segment and 2d point
    # todo: add test for 3d points should be handled planar
    for idx, coordinate in enumerate(line_data):
        if idx + 1 < len(line_data):
            y = coordinate[1] + 5
            projection = line.project(Point(0, y))
            assert projection.point_on_line.x == 3
            assert projection.point_on_line.y == y
            assert projection.point_on_line.z is None
            assert projection.distance_to_line_2d == 3
            assert projection.distance_to_line_3d is None
            assert projection.point_on_line.m == y
            assert projection.distance_along_line == y

    line_undershoot = line.cut(-1)
    assert line_undershoot.status == CutProfileStatus.undershoot
    assert line_undershoot.result is None
    assert line_undershoot.post_cut == line

    line_overshoot = line.cut(31)
    assert line_overshoot.status == CutProfileStatus.overshoot
    assert line_overshoot.result == line
    assert line_overshoot.post_cut is None

    line_cut = line.cut(5)
    assert line_cut.status == CutProfileStatus.valid
    assert line_cut.result.length_2d == 5
    assert line_cut.result.end_measure == 5
    assert line_cut.post_cut.length_2d == 25
    assert line_cut.post_cut.start_measure == 5
    assert line_cut.post_cut.end_measure == 30

    # todo: add more tests

    line_profile = line.cut_profile(-5, -1)
    assert line_profile.status == CutProfileStatus.invalid

    line_profile = line.cut_profile(31, 32)
    assert line_profile.status == CutProfileStatus.invalid

    line_profile = line.cut_profile(-1, 5)
    assert line_profile.status == CutProfileStatus.undershoot
    line_profile = line.cut_profile(1, 31)
    assert line_profile.status == CutProfileStatus.overshoot
    line_profile = line.cut_profile(-1, 31)
    assert line_profile.status == CutProfileStatus.under_and_overshoot
    line_profile = line.cut_profile(5, 10)
    assert line_profile.status == CutProfileStatus.valid


def test_3d_line_cut():
    # minimal edge case 3 as offset, same level line segments only on y and z offset
    line_data = [[3, 0, 0], [3, 10, 20], [3, 20, 40], [3, 30, 80]]
    distance = [0, 22.360679774997898, 44.721359549995796, 85.95241580617241]
    line = MeasureLineString(line_data)
    assert line.m_given is False

    for idx, coordinate in enumerate(line_data):
        assert line.line_measure_points[idx].coordinate_list() == coordinate
        assert line.line_measure_points[idx].m == distance[idx]

    assert line.length_2d == 30
    assert line.shapely.length == line.length_2d
    assert line.length_3d == 85.95241580617241
    assert line.end_measure == line.length_3d

    # minimal project test, use center of lin segment and 3d point
    # todo: add test for 2d points should be handled as same z as point on line
    expected_results = [
        [11.180339887498949, 10.44030650891055],
        [33.54101966249685, 30.14962686336267],
        [65.3368876780841, 60.07495318350236],
    ]
    for idx, coordinate in enumerate(line_data):
        if idx + 1 < len(line_data):
            y = coordinate[1] + 5
            projection = line.project(Point(0, y, 0))
            assert projection.point_on_line.z is not None
            assert projection.distance_along_line == expected_results[idx][0]
            assert projection.distance_to_line_2d == 3
            assert projection.distance_to_line_3d == expected_results[idx][1]
            assert projection.point_on_line.x == 3
            assert projection.point_on_line.y == y
            assert projection.point_on_line.m == expected_results[idx][0]

    line_cut = line.cut(-1)
    assert line_cut.status == CutProfileStatus.undershoot
    assert line_cut.post_cut == line

    line_cut = line.cut(100)
    assert line_cut.status == CutProfileStatus.overshoot
    assert line_cut.result == line
    assert line_cut.post_cut is None

    line_cut = line.cut(33)
    assert line_cut.status == CutProfileStatus.valid
    assert line_cut.result.start_measure == line.start_measure
    assert line_cut.post_cut.start_measure == line_cut.result.end_measure


def test_2d_line_m_cut():
    # minimal edge case 3 as offset, same level line segments only on y offset, increasing m with 100
    line_data = [[3, 0, 0], [3, 10, 100], [3, 20, 200], [3, 30, 300]]
    line = MeasureLineString(line_data, m_given=True)
    assert line.m_given is True

    for idx, coordinate in enumerate(line_data):
        assert line.line_measure_points[idx].coordinate_list() == coordinate[:2]
        assert line.line_measure_points[idx].m == coordinate[2]

    assert line.length_2d == 30
    assert line.length_3d is None
    assert line.end_measure == 300

    try:
        line.project(Point(0, 0))
    except NotImplementedError:
        assert True

    line_cut = line.cut(-1)
    assert line_cut.status == CutProfileStatus.undershoot
    assert line_cut.post_cut == line

    line_cut = line.cut(350)
    assert line_cut.status == CutProfileStatus.overshoot
    assert line_cut.result == line
    assert line_cut.post_cut is None

    line_cut = line.cut(150)
    assert line_cut.status == CutProfileStatus.valid
    assert line_cut.result.start_measure == line.start_measure
    assert line_cut.post_cut.start_measure == line_cut.result.end_measure


def test_3d_line_m_cut():
    # minimal edge case 3 as offset, same level line segments only on y and z offset, increasing m with 100
    line_data = [[3, 0, 0, 0], [3, 10, 20, 100], [3, 20, 40, 200], [3, 30, 80, 300]]
    line = MeasureLineString(line_data, m_given=True)
    assert line.m_given is True

    for idx, coordinate in enumerate(line_data):
        assert line.line_measure_points[idx].coordinate_list() == coordinate[:3]
        assert line.line_measure_points[idx].m == coordinate[3]

    assert line.length_2d == 30
    assert line.length_3d == 85.95241580617241
    assert line.end_measure == 300

    try:
        line.project(Point(0, 0))
    except NotImplementedError:
        assert True

    line_cut = line.cut(-1)
    assert line_cut.status == CutProfileStatus.undershoot
    assert line_cut.post_cut == line

    line_cut = line.cut(350)
    assert line_cut.status == CutProfileStatus.overshoot
    assert line_cut.result == line
    assert line_cut.post_cut is None

    line_cut = line.cut(150)
    assert line_cut.status == CutProfileStatus.valid
    assert line_cut.result.start_measure == line.start_measure
    assert line_cut.post_cut.start_measure == line_cut.result.end_measure


# def test_schema_line_m():
#     file_path = r""
#
#     with open(file_path) as f:
#         d = json.load(f)
#
#     for item in d["schemaRailConnectionFeatures"]:
#         coords = item["geometry"]["paths"][0]
#         coords.sort(key=lambda x: x[3], reverse=False)
#         line = MeasureLineString(coords, m_given=True)
#         acad.DrawShapelyObject(line.shapely)
#
#         acad.DrawText( item['attributes']['name'], line.shapely.centroid)
#         cut = line.end_measure * 0.2
#         measure_cut = line.cut_on_measure(cut)
#         # if measure_cut[0] is not None:
#         #     acad.DrawShapelyObject(measure_cut[0].shapely, color=5)
#         # if measure_cut[1] is not None:
#         #     acad.DrawShapelyObject(measure_cut[1].shapely, color=6)
#         if item['attributes']['key'] == "2c94c427-9cc7-41b7-82bb-038ff36c4242":
#             start = 500
#             end = 6000
#         else:
#             start = line.end_measure * 0.5
#             end = line.end_measure * 0.8
#         profile_cut = line.cut_profile(start, end)
#         acad.DrawShapelyObject(profile_cut.shapely, color=3)
