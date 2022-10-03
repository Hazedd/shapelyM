import array
import math

from pyautocad import APoint, Autocad
from shapely.geometry import LineString, MultiLineString, Point
from shapely.ops import linemerge


class AutocadUtilityService(object):
    def __init__(self):
        self.acad = Autocad(create_if_not_exists=True)
        # self.print_front()
        # print(self.acad.doc.Name)

    def print_front(self, text="Python connected\n"):
        self.acad.prompt(text)

    def _breakUp_autoCad_polyLine_coordinates(self, autoCadLineObject, numberOfCoordinates):
        res = tuple(
            autoCadLineObject.Coordinates[n : n + numberOfCoordinates]
            for n, i in enumerate(autoCadLineObject.Coordinates)
            if n % numberOfCoordinates == 0
        )
        return res

    def _get_shapely_from_cad_object(self, cad_object):
        if cad_object.ObjectName in ["AcDb3dPolyline"]:
            return LineString(self._breakUp_autoCad_polyLine_coordinates(cad_object, 3))
        elif cad_object.ObjectName in ["AcDbPolyline"]:
            return LineString(self._breakUp_autoCad_polyLine_coordinates(cad_object, 2))
        elif cad_object.ObjectName in ["AcDbPoint"]:
            return Point(cad_object.Coordinates)
        elif cad_object.ObjectName in ["AcDbLine"]:
            return LineString([cad_object.StartPoint, cad_object.EndPoint])

    def _draw_polyline2D(self, shapelyLineObject, color=None):
        points_2d = []
        for item in shapelyLineObject.coords[:]:
            points_2d.append(item[0])
            points_2d.append(item[1])
        points_double = array.array("d", points_2d)
        tester = self.acad.model.AddLightWeightPolyline(points_double)
        if color is not None:
            tester.Color = color

    def _draw_polyline3D(self, shapelyLineObject, color=None):
        points_3d = []
        for item in shapelyLineObject.coords[:]:
            points_3d.append(item[0])
            points_3d.append(item[1])

            if not math.isnan(item[2]):
                points_3d.append(item[2])
            else:
                points_3d.append(points_3d[-3])

        points_double = array.array("d", points_3d)
        tester = self.acad.model.Add3Dpoly(points_double)
        if color is not None:
            tester.Color = color

    def _draw_point(self, shapelyPointObject, color=None):
        if shapelyPointObject.has_z:
            p = APoint(shapelyPointObject.x, shapelyPointObject.y, shapelyPointObject.z)
            tester = self.acad.model.AddPoint(p)
        else:
            p = APoint(shapelyPointObject.x, shapelyPointObject.y)
            tester = self.acad.model.AddPoint(p)

        if color is not None:
            tester.Color = color

    def _profile_cutter(self, line, distance):
        if distance <= 0.0 or distance >= line.length:
            return [LineString(line)]
        coords = list(line.coords)
        for i, p in enumerate(coords):
            pd = line.project(Point(p))
            if pd == distance:
                return [LineString(coords[: i + 1]), LineString(coords[i:])]
            if pd > distance:
                cp = line.interpolate(distance)
                return [
                    LineString(coords[:i] + [(cp.x, cp.y, cp.z)]),
                    LineString([(cp.x, cp.y, cp.z)] + coords[i:]),
                ]

    def _get_multiLinestring_from_selection(self, selection):
        return MultiLineString(selection)

    def _merge_multiLinestring_to_linestring(self, shapelyMultiLinestringObject):
        # if 90'hoek recht omhoog zelfde xy maar z anders dan wordt vloeiende lijn... is dit ok?
        return linemerge(shapelyMultiLinestringObject)

    def _create_autocad_selection_get_shapely(self):
        selection = self.acad.get_selection()
        shapelyObjectList = []
        for item in selection:
            shapelyObjectList.append(self._get_shapely_from_cad_object(item))
        return shapelyObjectList


class AutocadService(object):
    def __init__(self):
        self.Utilities = AutocadUtilityService()

    def DrawShapelyObject(self, shapely_object, color: int = None):
        # todo: make annotation text somewhere on the geometry ???
        if shapely_object.geom_type == "LineString":
            if shapely_object.has_z:
                self.Utilities._draw_polyline3D(shapely_object, color)
            else:
                self.Utilities._draw_polyline2D(shapely_object, color)

        elif shapely_object.geom_type == "Point":
            self.Utilities._draw_point(shapely_object, color)

        # todo: implement multi linestring
        elif shapely_object.geom_type == "MultiLineString":
            for linestring in shapely_object:
                print(linestring)
                if linestring.has_z:
                    self.Utilities._draw_polyline3D(linestring)
                else:
                    self.Utilities._draw_polyline2D(linestring)

        # todo: not sure what to with a polygon in autocadService.....
        elif shapely_object.geom_type == "Polygon":
            raise NotImplementedError("Polygon")

        else:
            print(shapely_object.geom_type)
            raise NotImplementedError

    def GetShapelyListFromSelection(self):
        return self.Utilities._create_autocad_selection_get_shapely()

    def GetNormalisedLineStringFromSelection(self, reverse=False):
        shapelyObjectList = self.GetShapelyListFromSelection()
        return self.GetNormalisedLineStringFromShapelyList(shapelyObjectList)

    def GetNormalisedLineStringFromShapelyList(self, shapelyObjectList):
        # todo: make topology checks
        # todo: check if all polyline types 2d of 3d (if 1st in selection = 2d = output)
        multiLine = self.Utilities._get_multiLinestring_from_selection(shapelyObjectList)
        normalizedLine = self.Utilities._merge_multiLinestring_to_linestring(multiLine)
        return normalizedLine

    def ReverseLineString(self, lineObject):
        return LineString(lineObject.coords[::-1])

    def GetShapelyObjectCutLineAt2PointsOnLine(self, shapelyLineObject, fromDistance, toDistance):
        if toDistance <= fromDistance:
            raise ValueError("toDistance less or equeal as fromDistance")
        LineToEnd = LineString(
            [list(x.coords) for x in self.Utilities._profile_cutter(shapelyLineObject, toDistance)][0]
        )
        cutFrontAndEndPoint = [
            list(x.coords) for x in self.Utilities._profile_cutter(LineToEnd, fromDistance)
        ]
        if len(cutFrontAndEndPoint) <= 1:
            cuttedLine = LineString(cutFrontAndEndPoint[0])
        else:
            cuttedLine = LineString(cutFrontAndEndPoint[1])
        return cuttedLine

    def DrawProfileOverLine(self, shapelyLineObject, fromDistance, toDistance):
        cuttedLine = self.GetShapelyObjectCutLineAt2PointsOnLine(shapelyLineObject, fromDistance, toDistance)
        self.DrawShapelyObject(cuttedLine)
        return cuttedLine

    def DrawText(self, text_value, point=Point(), size=0.2):
        self.Utilities.acad.model.AddText(f"{text_value}", APoint(point.x, point.y), size)
