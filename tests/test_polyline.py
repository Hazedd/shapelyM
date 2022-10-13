from random import randint

import pytest
from shapely.geometry import LineString, Point
from shapely.ops import linemerge

from shapelyM.measureLineString import MeasureLineString
from shapelyM.measurePoint import MeasurePoint


class TestSimplePolyline:
    random_values_to_test = 10

    @pytest.fixture
    def simple_2d_line(self):
        line_data = [[3, 0], [3, 10], [3, 20], [3, 30]]
        fixture = MeasureLineString(line_data)
        return fixture

    @pytest.fixture
    def simple_3d_line(self):
        line_data = [[3, 0, 0], [3, 10, 0], [3, 20, 0], [3, 30, 0]]
        fixture = MeasureLineString(line_data)
        return fixture

    @pytest.fixture
    def simple_3d_line_z_increase(self):
        line_data = [[3, 0, 0], [3, 10, 10], [3, 20, 20], [3, 30, 30]]
        fixture = MeasureLineString(line_data)
        return fixture

    def test_init_2d(self, simple_2d_line):
        assert simple_2d_line is not None

    def test_init_3d(self, simple_3d_line):
        assert simple_3d_line is not None

    def test_length_2d(self, simple_2d_line):
        assert simple_2d_line.length_2d == 30
        assert simple_2d_line.length_3d == 30

    def test_length_3d(self, simple_3d_line):
        assert simple_3d_line.length_2d == 30
        assert simple_3d_line.length_3d == 30

    @pytest.mark.parametrize(
        "points",
        [
            MeasurePoint(randint(-100, 100), 31, randint(-1000, 10000))
            for i in range(0, random_values_to_test)
        ],
    )
    def test_measure_overshoot_3d(self, simple_3d_line, points):
        tester = simple_3d_line.project(points)
        assert tester.distance_along_line == simple_3d_line.length_3d

    @pytest.mark.parametrize(
        "points", [MeasurePoint(randint(-100, 100), 31) for i in range(0, random_values_to_test)]
    )
    def test_measure_overshoot_2d(self, simple_2d_line, points):
        tester = simple_2d_line.project(points)
        assert tester.distance_along_line == simple_2d_line.length_2d

    @pytest.mark.parametrize(
        "points",
        [
            MeasurePoint(randint(-100, 100), -1, randint(-1000, 10000))
            for i in range(0, random_values_to_test)
        ],
    )
    def test_measure_undershoot_3d(self, simple_3d_line, points):
        tester = simple_3d_line.project(points)
        assert tester.distance_along_line == 0

    @pytest.mark.parametrize(
        "points", [MeasurePoint(randint(-100, 100), -1) for i in range(0, random_values_to_test)]
    )
    def test_measure_undershoot_2d(self, simple_2d_line, points):
        tester = simple_2d_line.project(points)
        assert tester.distance_along_line == 0

    @pytest.mark.parametrize(
        "points",
        [
            [MeasurePoint(0, 5, 0), 7.0710678118654755],
            [MeasurePoint(0, 15, 0), 21.213203435596427],
            [MeasurePoint(0, 25, 0), 35.35533905932738],
        ],
    )
    def test_measure_between_vertices_3d(self, simple_3d_line_z_increase, points):
        tester = simple_3d_line_z_increase.project(points[0])
        assert tester.distance_along_line == points[1]

    @pytest.mark.parametrize(
        "points",
        [
            MeasurePoint(0, 5),
            MeasurePoint(0, 15),
            MeasurePoint(0, 25),
        ],
    )
    def test_measure_between_vertices_2d(self, simple_2d_line, points):
        assert simple_2d_line.project(points).distance_along_line == points.y

    @pytest.mark.parametrize(
        "points",
        [
            MeasurePoint(0, 0, 0),
            MeasurePoint(0, 10, 0),
            MeasurePoint(0, 20, 0),
            MeasurePoint(0, 30, 0),
        ],
    )
    def test_measure_on_vertices(self, simple_3d_line, points):
        tester = simple_3d_line.project(points)
        assert tester.distance_along_line == points.y

    @pytest.mark.parametrize(
        "points",
        [MeasurePoint(randint(-100, 100), 0, randint(-1000, 1000)) for i in range(0, random_values_to_test)],
    )
    def test_on_first_vertices(self, simple_3d_line, points):
        tester = simple_3d_line.project(points)
        assert tester.distance_along_line == 0

    @pytest.mark.parametrize(
        "points",
        [MeasurePoint(randint(-100, 100), 30, randint(-1000, 1000)) for i in range(0, random_values_to_test)],
    )
    def test_on_last_vertices(self, simple_3d_line, points):
        tester = simple_3d_line.project(points)
        assert tester.distance_along_line == 30

    @pytest.mark.parametrize(
        "points",
        [
            MeasurePoint(randint(-100, 100), randint(1, 9), randint(-1000, 1000))
            for i in range(0, random_values_to_test)
        ],
    )
    def test_on_first_part(self, simple_3d_line, points):
        tester = simple_3d_line.project(points)
        assert tester.distance_along_line < 10

    @pytest.mark.parametrize(
        "points",
        [
            MeasurePoint(randint(-100, 100), randint(21, 29), randint(-1000, 1000))
            for i in range(0, random_values_to_test)
        ],
    )
    def test_on_last_part(self, simple_3d_line, points):
        tester = simple_3d_line.project(points)
        assert tester.distance_along_line > 20


class TestComplexPolyline:
    def _split_string_data(self, string_data):
        return [list(map(float, x.split(","))) for x in string_data.split(" ")]

    def _create_line(self, string_data):
        line_data = self._split_string_data(string_data)
        return MeasureLineString(line_data)

    @pytest.fixture
    def complex_3d_line(self):
        string_data = (
            "161063.87,383689.249,20.346 160996.307,383682.013,20.475 160980.713,383680.732,20.51 "
            "160971.018,383680.123,20.527 160960.506,383679.646,20.558 160951.606,383679.382,20.581 "
            "160941.893,383679.249,20.582 160931.37,383679.275,20.618 160920.849,383679.492,20.635 "
            "160911.142,383679.852,20.659 160876.734,383682.401,20.767 160871.006,383682.891,20.727 "
            "160865.29,383683.494,20.739 160853.887,383684.978,20.754 160842.512,383686.724,20.808 "
            "160825.478,383689.569,20.844 160814.167,383691.641,20.851 160802.898,383693.932,20.87 "
            "160791.664,383696.422,20.89 160780.471,383699.058,20.909 160769.317,383701.847,20.928 "
            "160758.196,383704.8,20.964 160747.129,383707.939,20.985 160736.125,383711.272,21.02 "
            "160725.172,383714.789,21.051 160708.849,383720.378,21.072 160698.043,383724.308,21.11 "
            "160687.293,383728.411,21.122 160676.614,383732.685,21.165 160666.01,383737.128,21.174 "
            "160655.472,383741.74,21.208 160639.804,383748.969,21.238 160629.462,383753.992,21.252 "
            "160619.193,383759.182,21.304 160609.009,383764.532,21.317 160593.904,383772.855,21.348 "
            "160583.937,383778.607,21.378 160574.067,383784.512,21.403 160564.296,383790.571,21.419 "
            "160554.616,383796.788,21.459 160545.035,383803.157,21.482 160535.562,383809.674,21.496 "
            "160526.191,383816.341,21.54 160512.33,383826.622,21.589 160503.234,383833.653,21.608 "
            "160494.245,383840.83,21.637 160485.369,383848.153,21.65 160476.618,383855.61,21.658 "
            "160467.982,383863.204,21.702 160459.436,383870.916,21.717 160450.966,383878.708,21.755 "
            "160442.81,383886.578,21.764 160435.963,383893.441,21.803 160429.232,383900.418,21.829 "
            "160419.319,383911.061,21.856 160412.113,383918.993,21.873 160400.081,383932.541,21.907 "
            "160392.437,383941.395,21.934 160357.846,383982.748,22.069"
        )

        return self._create_line(string_data)

    @pytest.fixture
    def rail_connection_75t_line(self):
        # <RailConnection puic="ef5853f3-cae6-4a72-8ce0-7aa3fafdc5be" name="75T"

        # e0c2f8c4-78b2-4103-9660-16495f6e52e1 track 75T
        track_data = (
            "161756.813,383773.874,18.761 161940.82,383814.894,18.336 "
            "161964.502,383820.223,18.289 161984.591,383824.984,18.262 "
            "162002.608,383829.097,18.23 162007.296,383830.153,18.226 "
            "162051.151,383840.028,18.189 162351.515,383906.741,17.875 "
            "162361.406,383908.6,17.885 162378.35,383912.147,17.856 "
            "162404.107,383915.76,17.668"
        )
        track = LineString(self._split_string_data(track_data))

        # 2b7503eb-68c6-40d5-b4a0-1fe7e244a1f9 73 73BT
        passage_1_data = "161744.087,383771.054,18.761 161734.348,383768.896,18.761"
        passage_1 = LineString(self._split_string_data(passage_1_data))

        # cfdf040a-cbe6-4aa8-a8a4-27c980be27f2 73 T
        passage_2_data = "161756.813,383773.874,18.761 161744.087,383771.054,18.761"
        passage_2 = LineString(self._split_string_data(passage_2_data))

        # 82d77bb9-884e-4e46-ae32-da26b353f04f 225 R
        passage_3_data = (
            "162440.463,383918.65,17.668 162429.966,383917.815,17.668 162404.107,383915.76,17.668"
        )
        passage_3 = LineString(self._split_string_data(passage_3_data))
        rail_con = linemerge([passage_3, track, passage_1, passage_2])

        # reverse, to make sure its in right dwaring direction
        rail_con = LineString(list(rail_con.coords)[::-1])

        return MeasureLineString([item for item in rail_con.coords]), rail_con

    def test_complex_3d_line_length_2d(self, complex_3d_line):
        shape = complex_3d_line.shapely
        assert complex_3d_line.length_2d == shape.length

    def test_complex_3d_line_length_3d(self, complex_3d_line):
        assert complex_3d_line.length_3d == 804.7815548731708

    def test_rail_connection_75t_line_length(self, rail_connection_75t_line):
        length_ = rail_connection_75t_line[0].length_3d
        assert round(length_, 3) == 722.233

    @pytest.mark.parametrize(
        "points",
        [
            [162370.486, 383907.947, 17.868, 651.194],
            [161782.364, 383782.131, 18.701, 49.745],
            [162369.462, 383912.841, 17.868, 651.195],  # 651.194
            [161776.607, 383775.725, 18.701, 42.732],  # 42.733   / vertices
            [162378.350, 383912.147, 17.870, 659.752],
            [161773.130, 383777.512, 18.761, 39.728],
        ],
    )
    def test_rail_connection_75t_measures(self, rail_connection_75t_line, points):
        tester = rail_connection_75t_line[0].project(Point(points[0], points[1], points[2]))
        assert round(tester.distance_along_line, 3) == points[3]


class TestSideOfPolyline:
    random_values_to_test = 10

    @pytest.fixture
    def simple_3d_line_x(self):
        line_data = [[3, 0, 0], [3, 10, 10], [3, 20, 20], [3, 30, 30]]
        fixture = MeasureLineString(line_data)
        return fixture

    @pytest.fixture
    def simple_3d_line_y(self):
        line_data = [[0, 3, 0], [10, 3, 10], [20, 3, 20], [30, 3, 30]]
        fixture = MeasureLineString(line_data)
        return fixture

    #
    # 6, 6, -7

    @pytest.mark.parametrize(
        "points",
        [
            # Point([6, 3, -9])
            # Point([6, 30, 5])
            Point(6, randint(0, 30), randint(-10, 10))
            for i in range(0, random_values_to_test)
        ],
    )
    def test_right_of_line_x(self, simple_3d_line_x, points):
        tester = simple_3d_line_x.project(Point(points))
        assert tester.side_of_line == "Right"

    # @pytest.mark.parametrize(
    #     "points", [
    #         Point(0, randint(0, 30), randint(-10, 10))
    #         for i in range(0, random_values_to_test)
    #     ]
    # )
    # def test_left_of_line_x(self, simple_3d_line_x, points):
    #     tester = simple_3d_line_x.project(Point(points))
    #     assert tester.side_of_line == "Left"
