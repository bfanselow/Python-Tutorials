Python
=========

A random collection of python scripts, modules, and apps

/ LEARN
---------
Simple scripts to test/demonstrate some of the powerful, but trickier concepts in Python
- [listComprehension.py](https://github.com/bfanselow/Python/blob/master/LEARN/listComprehension.py)
- ``listSlicing.py``
- ``pandas_dataframe.py``

Examples
--------

  List Comprehension

    >>> import geopandas
    >>> from shapely.geometry import Polygon
    >>> p1 = Polygon([(0, 0), (1, 0), (1, 1)])
    >>> p2 = Polygon([(0, 0), (1, 0), (1, 1), (0, 1)])
    >>> p3 = Polygon([(2, 0), (3, 0), (3, 1), (2, 1)])
    >>> g = geopandas.GeoSeries([p1, p2, p3])

