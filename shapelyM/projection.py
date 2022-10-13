from __future__ import annotations

DEBUG = False
if DEBUG:  # pragma: no cover
    from debug.autocad import AutocadService

    acad = AutocadService()

#
#         if DEBUG:  # pragma: no cover
#             # draw input point
#             if point.z is not None:
#                 acad.DrawShapelyObject(Point(point.x, point.y, point.z))
#             else:
#                 acad.DrawShapelyObject(Point(point.x, point.y))
#             acad.DrawText(f"{self.side_of_line}", Point(point.x, point.y))
#
#             # draw line
#             if line_point_1.z is not None and line_point_2.z is not None:
#                 # acad.DrawText(f"start", Point(line_point_1.x, line_point_1.y))
#                 acad.DrawShapelyObject(
#                     LineString(
#                         [
#                             [line_point_1.x, line_point_1.y, line_point_1.z],
#                             [line_point_2.x, line_point_2.y, line_point_2.z],
#                         ]
#                     )
#                 )
#             else:
#                 acad.DrawShapelyObject(
#                     LineString([[line_point_1.x, line_point_1.y], [line_point_2.x, line_point_2.y]])
#                 )
#
#             # draw point on line
#             if self.point_on_line.z is not None:
#                 acad.DrawShapelyObject(
#                     Point(self.point_on_line.x, self.point_on_line.y, self.point_on_line.z)
#                 )
#             else:
#                 acad.DrawShapelyObject(Point(self.point_on_line.x, self.point_on_line.y))
#
#             # draw point to line
#             if self.point_on_line.z is not None and point.z is not None:
#                 acad.DrawShapelyObject(
#                     LineString(
#                         [
#                             [self.point_on_line.x, self.point_on_line.y, self.point_on_line.z],
#                             [point.x, point.y, point.z],
#                         ]
#                     )
#                 )
#             else:
#                 acad.DrawShapelyObject(
#                     LineString([[self.point_on_line.x, self.point_on_line.y], [point.x, point.y]])
#                 )
