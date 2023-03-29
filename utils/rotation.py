from math import radians
from typing import Any, Dict
import numpy as np


def cal_xy(module_pos, pad_pos, theta):
    """ Considering rotation
    """
    # calculate rotation matrix for each module

    real_pos = rotate(np.array(pad_pos), -theta)

    return (module_pos[0]+real_pos[0], module_pos[1]+real_pos[1])

def rotate(pos, theta):

    theta = radians(theta)
    c, s = np.cos(theta), np.sin(theta)
    R = np.array(((c, -s), (s, c)))
    
    return np.matmul(R, pos)

def cal_real_pad_vertices(pad_info: Dict[str, Any], clearance: float=0):
    corner_directions = [(-1,-1), (-1,1), (1,-1), (1,1)]
    if "relative_pos" in pad_info:
        center_relative = pad_info["relative_pos"]
        pad_size = [ps/2+clearance for ps in pad_info["size"]]
        theta = -pad_info["m_rotation"]
        module_pos = pad_info["module_pos"]

        relative_pos = []
        for d in corner_directions:
            size_xy = rotate((d[0]*pad_size[0], d[1]*pad_size[1]), pad_info["p_rotation"])
            relative_pos.append((center_relative[0]+size_xy[0], center_relative[1]+size_xy[1]))

        abs_pos = [rotate(np.array(p), theta) for p in relative_pos]
        real_vertex_pos = [(module_pos[0]+p[0], module_pos[1]+p[1]) for p in abs_pos]

    else:
        real_pos = pad_info["pos"]
        radius = pad_info["size"] / 2 + clearance
        real_vertex_pos = [(real_pos[0]+d[0]*radius, real_pos[1]+d[0]*radius) for d in corner_directions]

    return real_vertex_pos