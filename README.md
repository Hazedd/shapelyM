ShapelyM: linear referencing in 3D

The term linear referencing emerged from engineering applications where it was preferable to locate a point along a linear feature (often roads) by referencing that location to some other well-defined location, rather than using classical geographic coordinate systems. The most familiar illustration of linear referencing is the mile markers along U.S. highways (Federal Highway Administration 2001, Federal Transit Administration 2003).

Shapely is a BSD-licensed Python package for manipulation and analysis of planar geometric objects. It is based on the widely deployed GEOS (the engine of PostGIS) and JTS (from which GEOS is ported) libraries. It can be useful to specify position along linear features such as LineStrings and MultiLineStrings with a **1-dimensional** referencing system. Shapely supports linear referencing based on length or distance, evaluating the distance along a geometric object to the projection of a given point, or the point at a given distance along the object.

ShapelyM can be used to linear referencing in 3D.


## Usage:
```python
from shapelyM import LineStringMeasure, MeasurePoint
```

```python
line_measure = LineStringMeasure([[3, 0, 0], [3, 10, 0], [3, 20, 0], [3, 30, 0]])
projection = line_measure.project(Point(0, 5, 0))
```

returns:

```
{'point': MeasurePoint, 
 'point_on_line': MeasurePoint, 
 'distance_to_line': 5.830951894845301, 
 'distance_to_line_2d': 3.0, 
 'distance_along_line': 7.0710678118654755, 
 'side_of_line': 'Left'
 }
 ```

# Contribute

## Requirements 
New python project uses pyproject.toml to manage requerments and can be build by a newer build backend. 
For now we use flit https://flit.pypa.io/en/latest/index.html. Flit also doesn’t help you manage dependencies: you have to add them to pyproject.toml by hand. Tools like Poetry and Pipenv have features which help add and update dependencies on other packages. https://python-poetry.org/

## Build and Test
Install MakeFile for quality of life

After setting up a venv we use `make install` to build a fresh pulled repo

Code quality checks and testing needs to be passed and will be checked on every commit and in the pipeline. If code wont pass it wont commit so make sure to check it before with make check-all!

We use:
- pytest for testing, manual by `make test` in a console.
- flake8 and black for linting, manual by `make lint` in a console.
- myPy for typechecking, manual by `make typecheck` in a console.
- black and isort, manual by `make format` in a console.
- we use bumpversion for changing the version
- We can use pyAutocad for debug visualizing

We use flit as a build-backend and for managing (optional) dependencies.

## Testing
Make an effort to test each bit of functionality you add. Try to keep it simple.

### Links
- [make](https://www.gnu.org/software/make/manual/make.html)
- [flake8](https://flake8.pycqa.org/en/latest/)
- [black](https://github.com/psf/black)
- [myPy](https://mypy.readthedocs.io/en/stable/)
- [iSort](https://github.com/PyCQA/isort)
- [flit](https://flit.pypa.io/en/latest/)
- [bumpversion](https://github.com/peritus/bumpversion)
