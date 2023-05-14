import sys
sys.path.append('..')

from typing import Any, Dict, List
from Data_extraction.extract_kicad import PCB, extract_net_classes, extract_track_pieces
import json
import re
import os
import numpy as np
import math


def dump_to_PBCRDL_json(target_dir):
    def repl_func(match: re.Match):
        # JSON formatting helper
        return " ".join(match.group().split())
    
    kicad_file = os.path.join(target_dir, "processed.kicad_pcb")
    pcb = PCB(kicad_file)
    net_pads = extract_net_pads(pcb)
    net_classes = adjust_net_class(extract_net_classes(pcb.pcb))
    vias = extract_track_pieces(pcb.vias)
    dump = {
            "layers": pcb.layers, 
            "unit": "mm", # TODO: check where this is defined in kicad files
            "border": pcb.boundary_lines,
            # this is a list containing all the boundaries lines
            'nets': net_pads,
            'rules':{
                'net_classes': net_classes # TODO: is there a better way than extract_netclasses?
            },
            'solution': {
                'wires': extract_track_pieces(pcb.wires),
                'vias': [{
                    "position": v["at"],
                    "diameter": v["size"],
                    "layers": v["layers"],
                    "net": v["net"]
                } for v in vias]
            }
        }
    with open(f'{target_dir}final.json', 'w') as fd:
        s = json.dumps(dump,indent=2)
        s = re.sub("(?<=\[)[^\[\]]+(?=])", repl_func, s)
        fd.write(s)

def adjust_net_class(net_classes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    new_net_classes = []
    for nc in net_classes:
        new_nc = dict()
        new_nc["indices"] = nc["indices"]
        new_nc["width"] = nc["trace_width"]
        new_nc["clearance"] = nc["clearance"]
        new_nc["via_diameter"] = nc["via_dia"]
        new_net_classes.append(new_nc)
    return new_net_classes

def extract_net_pads(pcb: PCB) -> Dict[str, Any]:
    new_net_pads = dict()

    for net_idx, pads in pcb.net_pads.items():
        new_pads = []
        for pad_info in pads:
            tmp_pad_dict = {
                "type": pad_info["type"], 
                "layer": pad_info["pad_layer"],
                "shape": pad_info["shape"], 
                "center": pad_info["pad_center_xy"], 
                "radii": pad_info["pad_size"]
            }
            if pad_info["type"] == "circle":
                rotation = 0
            else:
                pad_vertices = pad_info["pad_vertices"]
                v1 = np.array(pad_vertices[1]) - np.array(pad_vertices[0])
                v2 = np.array(pad_vertices[2]) - np.array(pad_vertices[0])
                v3 = np.array(pad_vertices[3]) - np.array(pad_vertices[0])
                longest_edge = sorted([
                    (np.linalg.norm(v1, 2), tuple(v1)),
                    (np.linalg.norm(v2, 2), tuple(v2)),
                    (np.linalg.norm(v3, 2), tuple(v3))                    
                ])[1][1]
                longest_edge = - np.array(longest_edge) if longest_edge[0] < 0 else np.array(longest_edge)
                rotation = round(math.degrees(math.atan2(longest_edge[1],longest_edge[0])))
                rotation = rotation + 180 if rotation < 0 else rotation
            tmp_pad_dict["rotation"] = rotation
            new_pads.append(tmp_pad_dict)
        new_net_pads[net_idx] = new_pads
    
    return new_net_pads


if __name__ == "__main__":

    kicad_dir = sys.argv[1]
    dump_to_PBCRDL_json(target_dir=kicad_dir)
