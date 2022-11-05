from __future__ import annotations

from shapely.geometry import Point

from shapelyM.measureLineString import MeasureLineString

# import json


# todo: split below to fixtures and smaller test cases in test class


def test_2d_line():
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
    assert line.length_measure == 30

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

    assert line.cut(-1)[0] is None
    assert line.cut(-1)[1] == line
    # todo: add better test for cut_on_measure
    assert len(line.cut(5)) == 2
    assert line.cut(31)[0] == line
    assert line.cut(31)[1] is None
    assert line.cut_profile(3, 7).length_2d == 4.0


def test_3d_line():
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
    assert line.length_measure == line.length_3d

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

    assert line.cut(-1)[0] is None
    assert line.cut(-1)[1] == line
    # todo: add better test for cut_on_measure
    assert len(line.cut(5)) == 2
    assert line.cut(86)[1] is None
    assert line.cut(86)[0] == line

    assert line.cut_profile(3, 5).length_2d == 1.6169345316802266


def test_2d_line_m():
    # minimal edge case 3 as offset, same level line segments only on y offset, increasing m with 100
    line_data = [[3, 0, 0], [3, 10, 100], [3, 20, 200], [3, 30, 300]]
    line = MeasureLineString(line_data, m_given=True)
    assert line.m_given is True

    for idx, coordinate in enumerate(line_data):
        assert line.line_measure_points[idx].coordinate_list() == coordinate[:2]
        assert line.line_measure_points[idx].m == coordinate[2]

    assert line.length_2d == 30
    assert line.length_3d is None
    assert line.length_measure == 300

    try:
        line.project(Point(0, 0))
    except NotImplementedError:
        assert True

    # measure_cut = line.cut_on_measure(120)

    # acad.DrawShapelyObject(line.shapely)
    # if measure_cut[0] is not None:
    #     acad.DrawShapelyObject(measure_cut[0].shapely, color=5)
    # if measure_cut[1] is not None:
    #     acad.DrawShapelyObject(measure_cut[1].shapely, color=6)
    # profile_cut = line.cut_profile(250, 275)
    # acad.DrawShapelyObject(profile_cut.shapely, color=3)

    assert line.cut(-1)[0] is None
    assert line.cut(-1)[1] == line
    # todo: add better test for cut_on_measure
    assert len(line.cut(50))
    assert line.cut(301)[0] == line
    assert line.cut(301)[1] is None

    assert line.cut_profile(0, 50).length_2d == 5


def test_3d_line_m():
    # minimal edge case 3 as offset, same level line segments only on y and z offset, increasing m with 100
    line_data = [[3, 0, 0, 0], [3, 10, 20, 100], [3, 20, 40, 200], [3, 30, 80, 300]]
    line = MeasureLineString(line_data, m_given=True)
    assert line.m_given is True

    for idx, coordinate in enumerate(line_data):
        assert line.line_measure_points[idx].coordinate_list() == coordinate[:3]
        assert line.line_measure_points[idx].m == coordinate[3]

    assert line.length_2d == 30
    assert line.length_3d == 85.95241580617241
    assert line.length_measure == 300

    try:
        line.project(Point(0, 0))
    except NotImplementedError:
        assert True

    # todo: check in autocad

    assert line.cut(-1)[0] is None
    assert line.cut(-1)[1] == line
    # todo: add better test for cut_on_measure
    assert len(line.cut(50))
    assert line.cut(301)[0] == line
    assert line.cut(301)[1] is None

    assert line.cut_profile(0, 50).length_3d == 22.360679774997898


# from shapelyM.debug.autocad import AutocadService
# acad = AutocadService()
#
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
#         cut = line.length_measure * 0.2
#         measure_cut = line.cut_on_measure(cut)
#         # if measure_cut[0] is not None:
#         #     acad.DrawShapelyObject(measure_cut[0].shapely, color=5)
#         # if measure_cut[1] is not None:
#         #     acad.DrawShapelyObject(measure_cut[1].shapely, color=6)
#         if item['attributes']['key'] == "2c94c427-9cc7-41b7-82bb-038ff36c4242":
#             start = 500
#             end = 6000
#         else:
#             start = line.length_measure * 0.5
#             end = line.length_measure * 0.8
#         profile_cut = line.cut_profile(start, end)
#         acad.DrawShapelyObject(profile_cut.shapely, color=3)
