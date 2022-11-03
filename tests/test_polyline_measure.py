from __future__ import annotations

from shapely.geometry import Point

from shapelyM.measureLineString import MeasureLineString

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
            y_ = coordinate[1] + 5
            projection = line.project(Point(0, y_))
            assert projection.point_on_line.z is None
            assert projection.distance_along_line == y_
            assert projection.distance_to_line_2d == 3
            assert projection.distance_to_line_3d is None
            assert projection.point_on_line.x == 3
            assert projection.point_on_line.y == y_
            assert projection.point_on_line.m == y_

    assert line.cut_on_measure(-1)[0] == line
    # todo: add better test for cut_on_measure
    assert len(line.cut_on_measure(5)) == 2
    assert line.cut_on_measure(31)[0] == line
    assert line.cut_profile(3, 7).length_2d == 3


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
            y_ = coordinate[1] + 5
            projection = line.project(Point(0, y_, 0))
            assert projection.point_on_line.z is not None
            assert projection.distance_along_line == expected_results[idx][0]
            assert projection.distance_to_line_2d == 3
            assert projection.distance_to_line_3d == expected_results[idx][1]
            assert projection.point_on_line.x == 3
            assert projection.point_on_line.y == y_
            assert projection.point_on_line.m == expected_results[idx][0]

    assert line.cut_on_measure(-1)[0] == line
    # todo: add better test for cut_on_measure
    assert len(line.cut_on_measure(5)) == 2
    assert line.cut_on_measure(86)[0] == line

    assert line.cut_profile(3, 5).length_2d == 2


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

    assert line.cut_on_measure(-1)[0] == line
    # todo: add better test for cut_on_measure
    assert len(line.cut_on_measure(50))
    assert line.cut_on_measure(301)[0] == line

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

    assert line.cut_on_measure(-1)[0] == line
    # todo: add better test for cut_on_measure
    assert len(line.cut_on_measure(50))
    assert line.cut_on_measure(301)[0] == line

    assert line.cut_profile(0, 50).length_3d == 22.360679774997898
