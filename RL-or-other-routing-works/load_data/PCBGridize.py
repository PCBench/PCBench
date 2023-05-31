import sys
from typing import Any, Dict, List, Tuple
sys.path.append('..')

from utils.geometry import rotatePoint
import math
import numpy as np
from collections import defaultdict
from scipy.spatial.distance import euclidean


def pcb_range(border: List[Dict[str, Any]]) -> Tuple[float, float, float, float]:
    if len(border) == 0:
        print("This PCB is not defined with border!")
    xs, ys = [], []
    for line in border:
        if line["type"] == "polyline":
            xs += [line["start"][0], line["end"][0]]
            ys += [line["start"][1], line["end"][1]]
        elif line["type"] == "arc":
            radius = euclidean(line["start"], line["center"])
            xs += [line["center"][0] - radius, line["center"][0] + radius]
            ys += [line["center"][1] - radius, line["center"][1] + radius]
        elif line["type"] == "circle":
            xs += [line["center"][0] - line["radius"], line["center"][0] + line["radius"]]
            ys += [line["center"][1] - line["radius"], line["center"][1] + line["radius"]]
    
    return min(xs), max(xs), min(ys), max(ys)

def is_point_inside_pad(point: Tuple[float, float], pad: Dict[str, Any]) -> bool:
    counter_clockwose_angle = 360 - pad["rotation"]
    rotate_point = rotatePoint(centerPoint=pad["center"], point=point, angle=counter_clockwose_angle)
    if abs(rotate_point[0] - pad["center"][0]) < max(pad["radii"]) / 2 and abs(rotate_point[1] - pad["center"][1]) < min(pad["radii"]) / 2:
        return True 
    return False

def PCBGridize(pcb: Dict[str, Any], resolution: Tuple[float, float]):

    x_res, y_res = resolution
    min_x, max_x, min_y, max_y = pcb_range(pcb["border"])
    x_grid = int((max_x - min_x) / x_res) + 1
    y_grid = int((max_y - min_y) / y_res) + 1
    pcb_matrix = np.zeros((x_grid, y_grid, len(pcb["layers"])))
    layer_name2ID = {pcb['layers'][i]: i for i in range(len(pcb["layers"]))}
    nets = defaultdict(list)
    pad2region = defaultdict(set)
    for net_idx, pads in pcb["nets"].items():
        net_idx = int(net_idx)
        for pad in pads:
            pad_center_grid_x = int((pad["center"][0] - min_x) / x_res)
            pad_center_grid_y = int((pad["center"][1] - min_y) / y_res)
            if net_idx > 0:
                nets[net_idx] += [(pad_center_grid_x, pad_center_grid_y, layer_name2ID[ly]) for ly in pad["layer"]]

            pad_min_x = max(math.floor((pad["center"][0] - max(pad["radii"]) - min_x) / x_res), 0)
            pad_max_x = min(math.ceil((pad["center"][0] + max(pad["radii"]) - min_x) / x_res), x_grid-1)
            pad_min_y = max(math.floor((pad["center"][1] - max(pad["radii"]) - min_y) / y_res), 0)
            pad_max_y = min(math.ceil((pad["center"][1] + max(pad["radii"]) - min_y) / y_res), y_grid-1)
            for x in range(pad_min_x, pad_max_x + 1):
                for y in range(pad_min_y, pad_max_y + 1):
                    real_x, real_y = x * x_res + min_x, y * y_res + min_y
                    if is_point_inside_pad(point=(real_x, real_y), pad=pad):
                        for ly in pad["layer"]:
                            pcb_matrix[(x,y,layer_name2ID[ly])] = net_idx
                            if net_idx > 0:
                                pad2region[(pad_center_grid_x, pad_center_grid_y, layer_name2ID[ly])].add((x,y,layer_name2ID[ly]))
    return pcb_matrix, nets, pad2region