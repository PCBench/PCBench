from extract_kicad import PCB
import math
import numpy as np
from utils.geometry import is_point_inside_quadrilateral
from collections import defaultdict

def PCBGridize(pcb: PCB, resolution: float) -> None:

    min_x, min_y, max_x, max_y = tuple(pcb.circuit_range)
    x_grid = int((max_x - min_x) / resolution) + 1
    y_grid = int((max_y - min_y) / resolution) + 1
    pcb_matrix = np.zeros((x_grid, y_grid, len(pcb.layers)))
    layer_name2ID = {pcb.layers[i]: i for i in range(len(pcb.layers))}

    nets = defaultdict(list)

    for net_idx, pads in pcb.net_pads.items():
        for pad in pads:
            pad_min_x = math.floor((min([xy[0] for xy in pad["pad_vertices"]]) - min_x) / resolution)
            pad_max_x = math.ceil((max([xy[0] for xy in pad["pad_vertices"]]) - min_x) / resolution)
            pad_min_y = math.floor((min([xy[1] for xy in pad["pad_vertices"]]) - min_y) / resolution)
            pad_max_y = math.ceil((max([xy[1] for xy in pad["pad_vertices"]]) - min_y) / resolution)
            for x in range(pad_min_x, pad_max_x + 1):
                for y in range(pad_min_y, pad_max_y + 1):
                    pad_rect = pad["pad_vertices"]
                    if is_point_inside_quadrilateral(point=(x,y), quadrilateral=pad_rect):
                        pcb_matrix[(x,y,layer_name2ID[pad["pad_layer"]])] = net_idx
            
            if net_idx > 0:
                pad_center_grid_x = int((pad["pad_center_xy"][0] - min_x) / resolution)
                pad_center_grid_y = int((pad["pad_center_xy"][1] - min_y) / resolution)
                nets[net_idx].append((pad_center_grid_x, pad_center_grid_y, layer_name2ID[pad["pad_layer"]]))

    return pcb_matrix, nets


