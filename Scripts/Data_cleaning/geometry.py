from math import radians
from typing import List, Tuple
import numpy as np
from shapely.geometry import Polygon, Point
import math

def rotate(pos, theta):
    theta = radians(theta)
    c, s = np.cos(theta), np.sin(theta)
    R = np.array(((c, -s), (s, c)))
    
    return np.matmul(R, pos)


def closest_point_idx(points: List[Tuple[int, int, int]], given_point: Tuple[int, int, int]) -> int:
    # Convert list of points to a numpy array
    points = np.array(points)
    # Calculate Euclidean distance from given_point to each point in points
    distances = np.sqrt(np.sum((points - given_point)**2, axis=1))
    # Find the index of the closest point
    closest_idx = np.argmin(distances)
    # Return the closest point
    return closest_idx


def sort_quadrilateral_clockwise(vertices: List[Tuple[float, float]]) -> List[int]:
    p1, p2, p3, p4 = vertices[0], vertices[1], vertices[2], vertices[3]
    # Calculate the centroid of the quadrilateral
    cx = (p1[0] + p2[0] + p3[0] + p4[0]) / 4
    cy = (p1[1] + p2[1] + p3[1] + p4[1]) / 4

    # Calculate the angle of each point with respect to the centroid
    angles = [(i, (math.atan2(p[1] - cy, p[0] - cx) + 2 * math.pi) % (2 * math.pi)) for i, p in enumerate([p1, p2, p3, p4])]
    # Sort the points by angle in ascending order
    angles.sort(key=lambda x: x[1])

    # Sort the points in clockwise order
    return [angles[i][0] for i in [0, 1, 2, 3]]


def is_point_inside_quadrilateral(point: Tuple[float, float], quadrilateral: List[Tuple[float, float]]) -> bool:
    """
    Check if a 2D point is inside a quadrilateral. quadrilateral must be sorted clockwise or counter-clockwise
    """
    polygon = Polygon(quadrilateral)
    point = Point(point)
    return polygon.contains(point)
