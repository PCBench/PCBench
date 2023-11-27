import sys

from Scripts.Data_extraction.thirdparty.kicad_parser.kicad_pcb import KicadPCB
sys.path.append('..')

from typing import Any, Dict, List
from Data_extraction.extract_kicad import PCB
import json
import re
import os
import numpy as np
import math
import copy


def dump_to_PBCRDL_json(target_dir):
    def repl_func(match: re.Match):
        # JSON formatting helper
        return " ".join(match.group().split())
    
    kicad_file = os.path.join(target_dir, "processed.kicad_pcb")
    pcb = PCB(kicad_file)
    net_pads, keepouts = extract_net_pads(pcb)
    differential_pairs = copy.copy(pcb.differential_pairs)
    # differential_pairs = [[net_indices.index(dp[0]), net_indices.index(dp[1])] for dp in differential_pairs if dp[0] in net_indices and dp[1] in net_indices]
    net_classes = adjust_net_class(pcb.pcb, pcb.net_classes)
    dump = {
            "layers": pcb.layers, 
            "unit": "mm", # TODO: check where this is defined in kicad files
            "border": pcb.boundary_lines, # this is a list containing all the boundaries lines
            'nets': net_pads,
            'differential_pairs': differential_pairs,
            'keepouts': keepouts,
            'rules':{
                'net_classes': net_classes
            },
            'solution': {
                'wires': extract_wires(pcb.wires),
                'vias': extract_vias(pcb.vias)
            }
        }
    with open(os.path.join(target_dir, "final.json"), 'w') as fd:
        s = json.dumps(dump,indent=2)
        s = re.sub("(?<=\[)[^\[\]]+(?=])", repl_func, s)
        fd.write(s)

def extract_wires(wires):
    ret = []
    for wire in wires:
        wire_dict = dict()
        wire_dict["start"] = wire.start
        wire_dict["end"] = wire.end
        wire_dict["width"] = wire.width
        wire_dict["layer"] = wire.layer
        wire_dict["net"] = wire.net
        ret.append(wire_dict)
    return ret

def extract_vias(vias):
    ret = []
    for via in vias:
        via_dict = dict()
        via_dict["position"] = via.at
        via_dict["diameter"] = via.size
        via_dict["layers"] = via.layers
        via["net"] = via.net
        ret.append(via_dict)
    return ret

def adjust_net_class(pcb: KicadPCB, net_classes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    new_net_classes = []

    netname2idx = dict()
    for net_idx_name in pcb.net:
        if net_idx_name[1] == '""' or net_idx_name[1] == "":
            continue 
        netname2idx[str(net_idx_name[1])] = net_idx_name[0]

    visited_nets = set(['""', ""])
    # extract basic net info
    if net_classes is not None:
        for class_name, net_class in net_classes.items():
            if class_name == 'Default':
                continue
            new_nc = dict()
            new_nc["indices"] = [netname2idx[str(netname)] if not isinstance(netname, str) else netname2idx[netname] for netname in net_class['net_names']]
            new_nc["width"] = net_class["width"]
            new_nc["clearance"] = net_class["clearance"]
            new_nc["via_diameter"] = net_class["via_diameter"]
            new_net_classes.append(new_nc)
            visited_nets = visited_nets.union(set(net_class['net_names']))

        new_nc = dict()
        new_nc["indices"] = [netidx for netname, netidx in netname2idx.items() if netname not in visited_nets]
        new_nc["width"] = net_classes["Default"]["width"]
        new_nc["clearance"] = net_classes["Default"]["clearance"]
        new_nc["via_diameter"] = net_classes["Default"]["via_diameter"]
        if len(new_nc["indices"]) > 0:
            new_net_classes.append(new_nc)
    return new_net_classes

def extract_net_pads(pcb: PCB) -> Dict[str, Any]:
    new_net_pads = dict()
    # net_indices = []
    # new_net_pads = []
    keepouts = []
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
        if net_idx == -1:
            keepouts = new_pads
        else:
            new_net_pads[net_idx] = new_pads
    
    return new_net_pads, keepouts


if __name__ == "__main__":

    kicad_dir = sys.argv[1]
    dump_to_PBCRDL_json(target_dir=kicad_dir)
