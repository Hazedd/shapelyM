from __future__ import annotations

import numpy as np

from shapelyM.measurePoint import MeasurePoint


def point_on_line(
    a: MeasurePoint, b: MeasurePoint, p: MeasurePoint, belong_to_segment=False
) -> np.array:
    """Ettetet.

    # todo: make sure:
        - should handle shapely Points
        - handle Projection on 2d, then add height:
          solution in linear_reference_point_on_line is ugly ... it woks

    :param a:
    :param b:
    :param p:
    :param belong_to_segment:
    :return:
    """
    if a.x == b.x and a.y == b.y:
        return np.array([a.x, a.y, a.z])

    if a.z is not None and b.z is not None and p.z is not None:
        a = np.array([a.x, a.y, a.z])
        b = np.array([b.x, b.y, b.z])
        p = np.array([p.x, p.y, p.z])

    else:
        a = np.array([a.x, a.y])
        b = np.array([b.x, b.y])
        p = np.array([p.x, p.y])

    ap = p - a
    ab = b - a
    if not belong_to_segment:
        return a + np.dot(ap, ab) / np.dot(ab, ab) * ab
    else:
        t = np.dot(ap, ab) / np.dot(ab, ab)
        t = max(0, min(1, t))
        return a + t * ab


def is_between(a: MeasurePoint, b: MeasurePoint, c: MeasurePoint) -> bool:
    """A asdsdsd.

    # todo: make sure it handles 3d.

    :param a:
    :param b:
    :param c:
    :return:
    """

    cross_product = (c.y - a.y) * (b.x - a.x) - (c.x - a.x) * (b.y - a.y)

    # compare versus epsilon for floating point values, or != 0 if using integers
    if abs(cross_product) > 0.0000001:  # sys.float_info.epsilon:
        return False

    dot_product = (c.x - a.x) * (b.x - a.x) + (c.y - a.y) * (b.y - a.y)
    if dot_product < 0:
        return False

    squared_length_ba = (b.x - a.x) * (b.x - a.x) + (b.y - a.y) * (b.y - a.y)
    if dot_product > squared_length_ba:
        return False

    return True
