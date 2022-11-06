from shapely.geometry import LineString
from shapelyAcad.autocad import ShapelyAcad

from shapelyM import LineProjection, MeasureLineString, MeasurePoint

acad = ShapelyAcad()

# todo: add color


def draw_measure_point_in_autocad(measure_point: MeasurePoint, suffix: str = ""):
    """Debug methode to draw shapley.Point in autocad."""
    shapely_point = measure_point.shapely()
    acad.draw_text(
        f"x:{measure_point.x}, y:{measure_point.y}, z:{measure_point.z}, m:{measure_point.m}, {suffix}",
        shapely_point,
    )


def draw_measure_line_in_autocad(measure_line: MeasureLineString):
    """Debug methode to draw shapley.LineString in autocad."""
    acad.draw_shapely(measure_line.shapely)
    for measure_point in measure_line.line_measure_points:
        draw_measure_point_in_autocad(measure_point)


# def draw_profile_in_autocad(measure_line: MeasureLineString):
#     """Debug methode to draw Profile in autocad."""
#     pass


def draw_projection_in_autocad(line_projection: LineProjection):
    """Debug methode to draw LineProjection in autocad."""
    draw_measure_point_in_autocad(line_projection.point, f"side: {line_projection.side_of_line.value}")
    draw_measure_point_in_autocad(line_projection.point_on_line)
    acad.draw_shapely(
        LineString(
            [
                line_projection.point_on_line.shapely(),
                line_projection.point.shapely(),
            ]
        )
    )
