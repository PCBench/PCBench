from typing import Any, Dict, List, Optional, Set, Tuple
import collections
from .thirdparty.kicad_parser.kicad_pcb import *
from .thirdparty.kicad_parser.sexp_parser import *
from .utils.pad_rotation import calculate_pad_pos_size, cal_xy
from scipy.spatial import distance
import math

class PCB:
    def __init__(
            self, 
            kicad_file: str="../../PCBs/1Bitsy_1bitsy/raw.kicad_pcb", 
            delete_nets: Optional[Set[str]]=None
        ) -> None:
        self.file = kicad_file
        self.obs_pad_value = -1
        self.via_obs_pad_value = -2
        self.pcb, self.net_classes = KicadPCB.load(kicad_file)
        self.kicad_version = self.pcb.version
        self.max_layer_index = 16 if self.kicad_version == 3 else 32
        self.layers = extract_layer(pcb=self.pcb, max_layer_index=self.max_layer_index)

        # extract boundary info: circuit region and boundary lines with width
        lines = extract_bound(self.pcb)
        self.boundary_lines = lines

        # extract net info: net indices, pads with their regions
        self.net_indices = extract_nets_indices(self.pcb, delete_nets=delete_nets)
        self.net_pads = extract_net_pads(
            pcb=self.pcb, 
            layers=self.layers, 
            exclude_nets=[self.via_obs_pad_value],
            net_indices=self.net_indices,
            obs_pad_value=self.obs_pad_value
        )
        self.nets_info, self.differential_pairs = extract_net_info(pcb=self.pcb, net_indices=self.net_indices, net_classes=self.net_classes)
        # TODO: self.pcb.arcs?
        self.wires = self.pcb.segment if "segment" in self.pcb else []
        self.vias = self.pcb.via if "via" in self.pcb else []

    @property
    def net_pads(self):
        return self._net_pads
    
    @net_pads.setter
    def net_pads(self, value):
        self._net_pads = value
    
    @property
    def wires(self):
        return self._wires
    
    @wires.setter
    def wires(self, value):
        self._wires = value

    @property
    def vias(self):
        return self._vias
    
    @vias.setter
    def vias(self, value):
        self._vias = value
    
    @property
    def nets_info(self):
        return self._nets_info
    
    @nets_info.setter
    def nets_info(self, value):
        self._nets_info = value

def replace_last_plus_with_minus(input_string):
    # Find the last occurrence of "+"
    last_plus_index = input_string.rfind("+")

    # Check if "+" is found in the string
    if last_plus_index != -1:
        # Replace the last "+" with "-"
        modified_string = input_string[:last_plus_index] + "-" + input_string[last_plus_index + 1:]
        return modified_string
    else:
        # If "+" is not found, return the original string
        return input_string


def extract_net_info(pcb: KicadPCB, net_indices: Set[int], net_classes: Dict[str, Any]) -> Tuple[Dict[int, Any], List[Tuple[int, int]]]:
    nets_info = dict()

    netname2idx = dict()
    for net_idx_name in pcb.net:
        nets_info[net_idx_name[0]] = dict()
        nets_info[net_idx_name[0]]["net_name"] = net_idx_name[1]
        netname2idx[str(net_idx_name[1])] = net_idx_name[0]
    differential_pairs = []
    # extract differential pairs
    for name in netname2idx:
        if "+" in name and replace_last_plus_with_minus(name) in netname2idx:
            differential_pairs.append((netname2idx[name], netname2idx[replace_last_plus_with_minus(name)]))

    visited_nets = set(['""', ""])
    # extract basic net info
    if net_classes is not None:
        for _, net_class in net_classes.items():
            for netname in net_class['net_names']:
                visited_nets.add(netname)
                netidx = netname2idx[str(netname)] if not isinstance(netname, str) else netname2idx[netname]
                nets_info[netidx]["clearance"] = net_class['clearance']
                nets_info[netidx]["trace_width"] = net_class['width']
                nets_info[netidx]["via_dia"] = net_class['via_diameter']
        for netname, netidx in netname2idx.items():
            if netname not in visited_nets:
                nets_info[netidx]["clearance"] = net_classes["Default"]['clearance']
                nets_info[netidx]["trace_width"] = net_classes["Default"]['width']
                nets_info[netidx]["via_dia"] = net_classes["Default"]['via_diameter']
    else:
        print(f"there is no default net class, setting clearance manually!!")
        for netidx in net_indices:
            nets_info[netidx]["clearance"] = 0.12
            nets_info[netidx]["trace_width"] = 0.3
            nets_info[netidx]["via_dia"] = 0.5
            # nets_info[netidx]["via_drill"] = 0.35
            # nets_info[netidx]["uvia_dia"] = 0.3
            # nets_info[netidx]["uvia_drill"] = 0.1
    return nets_info, differential_pairs
    
def extract_nets_indices(pcb: KicadPCB, delete_nets: Optional[Set[str]]=None) -> Set[int]:

    all_net_indices = set([n[0] for n in pcb["net"]])
    module_nets = collections.defaultdict(int)

    modules = pcb.footprint if pcb.version > 20211000 else pcb.module
    for module in modules:
        # pos = tuple(module.at)
        for p in module.pad:
            if "net" in p:
                module_nets[p["net"][0]] += 1
                if delete_nets is not None and p["net"][1] in delete_nets:
                    module_nets[p["net"][0]] = 0

    tmp_nets = list(all_net_indices)
    for net_idx in tmp_nets:
        if module_nets[net_idx]<=1:
            all_net_indices.remove(net_idx)

    return all_net_indices

def extract_layer(pcb: KicadPCB, max_layer_index: int) -> List[str]:
    
    layers = list()
    layer_indices = []
    for k in pcb.layers:
        if int(k) < max_layer_index:
            layer_indices.append(int(k))
            layers.append(pcb.layers[k][0])
    
    return [x for _, x in sorted(zip(layer_indices, layers))]

def extract_net_pads(pcb: KicadPCB, 
                     layers: List[str], 
                     exclude_nets: List[int],
                     net_indices: Set[int],
                     obs_pad_value: int
                    ) -> Dict[float, List[Any]]:

    net2pads = collections.defaultdict(list)

    modules = pcb.footprint if pcb.version > 20211000 else pcb.module
    for i_m, module in enumerate(modules):
        module_pos = tuple(module.at)
        for i_p, p in enumerate(module.pad):
            pads_info = extract_pad(p, module_pos, layers, net_indices, obs_pad_value)
            for p_info in pads_info:
                p_info[1]["m_p_index"] = (i_m, i_p)  # record module index and pad index for cleaning up
                net2pads[p_info[0]].append(p_info[1])

    new_net2pads = calculate_pad_pos_size(net2pads, exclude_nets)
    
    # for via in self.pcb.via:
    #     pads_info = self.extract_single_via_pad(via)
    #     for pad_info in pads_info:
    #         net2pads[self.via_obs_pad_value].append(pad_info[1])

    return new_net2pads

def extract_pad(
        module_pad: Dict[str, List[Any]], 
        module_pos: Any, 
        layers: List[str],
        net_indices: Set[int],
        obs_pad_value: int
    ) -> List[Any]:

    pad_net_idx = module_pad["net"][0] if "net" in module_pad and module_pad["net"][0] in net_indices else obs_pad_value
    # pad_shape = module_pad[2]
    m_rotation = module_pos[2] if len(module_pos)==3 else 0

    ret_pads = []   # return 2 pads info if it is a drill hole
    if "layers" not in module_pad:
        return ret_pads

    pad_info = {}
    p_rotation = module_pad["at"][2] if len(module_pad["at"])==3 else 0
    pad_info["type"] = module_pad[1]
    pad_info["relative_pos"] = tuple(module_pad["at"])[:2]
    pad_info["size"] = tuple(module_pad["size"])
    pad_info["shape"] = module_pad[2]
    pad_info["m_rotation"] = m_rotation
    pad_info["p_rotation"] = p_rotation - m_rotation
    pad_info["module_pos"] = tuple(module_pos)[:2]
    pad_info["layer"] = []
    for pl in module_pad.layers:
        if pl == "*.Cu" or pl == '"*.Cu"':
            pad_info["layer"] = layers
            break
        elif pl in layers:
            pad_info["layer"].append(pl)
    pad_info["drill_hole"] = False if pad_info["layer"]==1 else True
    ret_pads.append([pad_net_idx, pad_info])

    return ret_pads

def calculate_arc_end_point(start_point, center, angle):
    # Convert angle from degrees to radians
    angle_rad = math.radians(angle)
    
    # Translate start point and center to origin
    translated_start = start_point[0] - center[0], start_point[1] - center[1]
    
    # Calculate the end point coordinates
    end_x = translated_start[0] * math.cos(angle_rad) - translated_start[1] * math.sin(angle_rad)
    end_y = translated_start[0] * math.sin(angle_rad) + translated_start[1] * math.cos(angle_rad)
    
    # Translate the end point back to the original coordinate system
    end_point = end_x + center[0], end_y + center[1]
    
    return end_point

def extract_bound(pcb: KicadPCB) -> Tuple[float, float, float, float, List[Any]]:

    gr_lines = pcb.gr_line
    gr_arcs = pcb.gr_arc
    gr_circles = pcb.gr_circle

    lines = []
    width = 0
    for line in gr_lines:
        if line["layer"][1:-1] == "Edge.Cuts" or line["layer"] == "Edge.Cuts":
            width = line.width if "width" in line else line.stroke.width
            lines.append({"type":"polyline", "vertices":[tuple(line.start), tuple(line.end)]})
    # for arcs in gr_arcs:
    #     if arcs["layer"][1:-1] == "Edge.Cuts" or arcs["layer"] == "Edge.Cuts":
    #         width = arcs.width if "width" in arcs else arcs.stroke.width
    #         lines.append({"type":"arc", "start":tuple(arcs.start), "center":tuple(arcs.end), "clockwise_angle":arcs.angle})
    
    # for circle in gr_circles:
    #     if circle["layer"][1:-1] == "Edge.Cuts" or circle["layer"] == "Edge.Cuts":
    #         width = circle.width if "width" in circle else circle.stroke.width  # kicad v5 vs v6
    #         radius = distance.euclidean(tuple(circle.end), tuple(circle.center))
    #         lines.append({"type":"circle", "center":tuple(circle.center), "radius":radius})

    for arcs in gr_arcs:
        if arcs["layer"][1:-1] == "Edge.Cuts" or arcs["layer"] == "Edge.Cuts":
            width = arcs.width if "width" in arcs else arcs.stroke.width
            radius = distance.euclidean(tuple(arcs.end), tuple(arcs.start))
            end = calculate_arc_end_point(tuple(arcs.start), tuple(arcs.end), arcs.angle)
            lines.append({"type":"arc", "vertices":[tuple(arcs.start), end], "radius":radius})
    
    for circle in gr_circles:
        if circle["layer"][1:-1] == "Edge.Cuts" or circle["layer"] == "Edge.Cuts":
            width = circle.width if "width" in circle else circle.stroke.width  # kicad v5 vs v6
            radius = distance.euclidean(tuple(circle.end), tuple(circle.center))
            lines.append({"type":"circle", "vertices":[tuple(circle.end), tuple(circle.center)], "radius":radius})

    modules = pcb.footprint if pcb.version > 20211000 else pcb.module
    for module in modules:
        m_x, m_y = module.at[0], module.at[1]
        angle = module.at[2] if len(module.at) == 3 else 0
        if "fp_line" in module:
            for line in module.fp_line:
                if not isinstance(line, str) and line.layer == "Edge.Cuts":
                    width = line.width if "width" in line else line.stroke.width  # kicad v5 vs v7
                    lines.append({"type":"polyline", "vertices":[cal_xy([m_x, m_y], line.start, angle), cal_xy([m_x, m_y], line.end, angle)]})
                    # lines.append({"type":"polyline", "start":cal_xy([m_x, m_y], line.start, angle), "end":cal_xy([m_x, m_y], line.end, angle)})
                    # print({"type":"polyline", "vertices":[(line.start[0] + m_x, line.start[1] + m_y), (line.end[0] + m_x, line.end[1] + m_y)]})
        if "fp_arc" in module:
            for arc in module.fp_arc:
                if not isinstance(arc, str) and arc.layer == "Edge.Cuts":
                    width = arc.width if "width" in arc else arc.stroke.width
                    arc_start = cal_xy([m_x, m_y], arc.start, angle)
                    arc_end = cal_xy([m_x, m_y], arc.end, angle)
                    radius = distance.euclidean(tuple(arc_end), tuple(arc_start))
                    end = calculate_arc_end_point(tuple(arc_start), tuple(arc_end), arc.angle)
                    lines.append({"type":"arc", "vertices":[tuple(arc_start), end], "radius":radius})
        if "fp_circle" in module:
            for circle in module.fp_circle:
                if not isinstance(circle, str) and circle.layer == "Edge.Cuts":
                    width = circle.width if "width" in circle else circle.stroke.width  # kicad v5 vs v6
                    circle_end = cal_xy([m_x, m_y], circle.end, angle)
                    circle_center = cal_xy([m_x, m_y], circle.center, angle)
                    radius = distance.euclidean(tuple(circle_end), tuple(circle_center))
                    lines.append({"type":"circle", "vertices":[tuple(circle_end), tuple(circle_center)], "radius":radius}) 
    return lines

def extract_single_via_pad(via_info: Dict[str, Any]) -> List[Any]:
    ret_pads = []
    for p_l in via_info["layers"]:
        pad_info = {
            "pos": via_info["at"], 
            "size": via_info["size"], 
            "drill": via_info["drill"], 
            "layer": p_l, 
            "drill_hole": False
        }
        ret_pads.append([via_info["net"], pad_info])
    return ret_pads

