
from typing import Any, Dict, List, Tuple
import numpy as np
from .geometry import rotate

def cal_xy(module_pos, pad_pos, theta):
    """ Considering rotation
    """
    # calculate rotation matrix for each module

    real_pos = rotate(np.array(pad_pos), -theta)

    return (module_pos[0]+real_pos[0], module_pos[1]+real_pos[1])

def cal_real_pad_vertices(pad_info: Dict[str, Any], clearance: float=0) -> List[Tuple[float, float]]:
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

def calculate_pad_pos_size(net2pads_raw: Dict[float, List[Any]], exclude_nets: List[float]) -> Dict[float, List[Any]]:
    net2pads_new = dict()
    for netidx, pads in net2pads_raw.items():
        if netidx not in exclude_nets:
            net2pads_new[netidx] = []
            for pad in pads:
                pad_xy = cal_xy(pad["module_pos"], pad["relative_pos"], pad["m_rotation"])
                pad_vertices = cal_real_pad_vertices(pad)
                net2pads_new[netidx].append({
                    "pad_center_xy": pad_xy, 
                    "pad_vertices": pad_vertices,
                    "pad_size": pad["size"],
                    "pad_layer": pad["layer"],
                    "drill_hole": pad["drill_hole"]})
        else:
            net2pads_new[netidx] = pads
    return net2pads_new 