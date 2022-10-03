ShapelyM: linear referencing in 3D

The term linear referencing emerged from engineering applications where it was preferable to locate a point along a linear feature (often roads) by referencing that location to some other well-defined location, rather than using classical geographic coordinate systems. The most familiar illustration of linear referencing is the mile markers along U.S. highways (Federal Highway Administration 2001, Federal Transit Administration 2003).

Shapely is a BSD-licensed Python package for manipulation and analysis of planar geometric objects. It is based on the widely deployed GEOS (the engine of PostGIS) and JTS (from which GEOS is ported) libraries. It can be useful to specify position along linear features such as LineStrings and MultiLineStrings with a **1-dimensional** referencing system. Shapely supports linear referencing based on length or distance, evaluating the distance along a geometric object to the projection of a given point, or the point at a given distance along the object.

ShapelyM can be used to linear referencing in 3D.

todo:
 - install and import libary
 - usage with shapely
 - usage standalone

 - next features:
   - 1
   - 2
 