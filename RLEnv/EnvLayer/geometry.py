from math import radians
from typing import List, Tuple
import numpy as np
import math
from scipy.spatial.distance import euclidean

ACCURACY_COMPENSATION = 1e-4

def rotatePoint(centerPoint: Tuple[float, float], point: Tuple[float, float], angle: float) -> Tuple[float, float]:
    """Rotates a point around another centerPoint. Angle is in degrees.
    Rotation is counter-clockwise"""
    angle = radians(angle)
    temp_point = point[0]-centerPoint[0] , point[1]-centerPoint[1]
    temp_point = ( temp_point[0]*math.cos(angle)-temp_point[1]*math.sin(angle) , temp_point[0]*math.sin(angle)+temp_point[1]*math.cos(angle))
    temp_point = temp_point[0]+centerPoint[0] , temp_point[1]+centerPoint[1]
    return temp_point

def closest_point_idx(points: List[Tuple[int, int, int]], given_point: Tuple[int, int, int]) -> int:
    # Convert list of points to a numpy array
    points = np.array(points)
    # Calculate Euclidean distance from given_point to each point in points
    try:
        distances = np.sqrt(np.sum((points - given_point)**2, axis=1))
    except:
        print(points, given_point)

    # Find the index of the closest point
    closest_idx = np.argmin(distances)
    # Return the closest point
    return closest_idx

def nodes_inside_rectangle(
        start: Tuple[int, int], 
        end: Tuple[int, int], 
        width: float,
        resolution: Tuple[float, float]
    ) -> List[Tuple[int, int]]:
    """ To find grid nodes inside a rectangle
        start: start point of a wire segment
        end: end point of a wire segment
        width: wire width + clearance (mm)
    """
    inside_nodes = []
    half_width = width / 2 / min(resolution)
    min_x = int(min(start[0] - half_width, end[0] - half_width))
    max_x = int(max(start[0] + half_width, end[0] + half_width))
    min_y = int(min(start[1] - half_width, end[1] - half_width))
    max_y = int(max(start[1] + half_width, end[1] + half_width))

    angle = math.degrees(math.atan2(end[1] - start[1], end[0] - start[0]))
    center = ((start[0] + end[0]) / 2 * resolution[0], (start[1] + end[1]) / 2 * resolution[1])
    for x in range(min_x, max_x + 1):
        for y in range(min_y, max_y + 1):
            rp = rotatePoint(centerPoint=center, point=(x * resolution[0], y * resolution[1]), angle=angle)
            if abs(rp[0] - center[0]) <= abs(euclidean(start, end) / 2 * resolution[0]) + ACCURACY_COMPENSATION and abs(rp[1] - center[1]) <= width / 2:
                inside_nodes.append((x,y))

    return inside_nodes

def nodes_inside_circle(
        center: Tuple[int, int], 
        diameter: float, 
        resolution: Tuple[float, float]
    ) -> List[Tuple[int, int]]:
    inside_nodes = []
    semi_dia = diameter / 2 / min(resolution)
    min_x = int(center[0] - semi_dia)
    max_x = int(center[0] + semi_dia)
    min_y = int(center[1] - semi_dia)
    max_y = int(center[1] + semi_dia)

    for x in range(min_x, max_x + 1):
        for y in range(min_y, max_y + 1):
            if euclidean((x * resolution[0], y * resolution[1]), (center[0] * resolution[0], center[1] * resolution[1])) <= diameter / 2:
                inside_nodes.append((x,y))
    return inside_nodes