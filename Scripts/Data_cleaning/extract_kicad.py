from typing import Any, Dict, List, Optional, Set, Tuple
import collections
from kicad_pcb import *
from sexp_parser import *
from pad_rotation import calculate_pad_pos_size


class PCB:
    def __init__(
            self, 
            kicad_file: str="benchmarks/real_world/1bitsy.kicad_pcb", 
            delete_nets: Optional[Set[str]]=None
        ) -> None:

        self.obs_pad_value = -1
        self.via_obs_pad_value = -2
        self.pcb = KicadPCB.load(kicad_file)

        self.layers = extract_layer(pcb=self.pcb)

        # extract boundary info: circuit region and boundary lines with width
        min_x, min_y, max_x, max_y, lines = extract_bound(self.pcb.gr_line, self.pcb.gr_arc)
        self.circuit_range = [min_x, min_y, max_x, max_y]
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
        self.nets_info, self.differential_pairs = extract_net_info(pcb=self.pcb, net_indices=self.net_indices)
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


def extract_net_info(pcb: KicadPCB, net_indices: Set[int]) -> Tuple[Dict[int, Any], List[Tuple[int, int]]]:
    nets_info = dict()

    netname2idx = dict()
    for net_idx_name in pcb.net:
        nets_info[net_idx_name[0]] = dict()
        nets_info[net_idx_name[0]]["net_name"] = net_idx_name[1]
        netname2idx[net_idx_name[1]] = net_idx_name[0]
    
    differential_pairs = []
    # extract differential pairs
    for name in netname2idx:
        if "-" == name[-1] and name[:-1] + "+" in netname2idx:
            differential_pairs.append((netname2idx[name], netname2idx[name[:-1]+"+"]))
    
    # extract basic net info
    if "net_class" in pcb:
        for net_class in pcb.net_class:
            if "add_net" in net_class: 
                net_names = net_class['add_net']
            else:
                net_names = netname2idx.keys()
            for netname in net_names:
                netidx = netname2idx[str(netname)]
                nets_info[netidx]["clearance"] = net_class['clearance']
                nets_info[netidx]["trace_width"] = net_class['trace_width']
                nets_info[netidx]["via_dia"] = net_class['via_dia']
                nets_info[netidx]["via_drill"] = net_class['via_drill']
                try:
                    nets_info[netidx]["uvia_dia"] = net_class['uvia_dia']
                    nets_info[netidx]["uvia_drill"] = net_class['uvia_drill']
                except:
                    print("There is no uvia in the net class!!!")
    else:
        print(f"there is no default net class, setting clearance manually!!")
        for netidx in net_indices:
            nets_info[netidx]["clearance"] = 0.12
            nets_info[netidx]["trace_width"] = 0.3
            nets_info[netidx]["via_dia"] = 0.5
            nets_info[netidx]["via_drill"] = 0.35
            nets_info[netidx]["uvia_dia"] = 0.3
            nets_info[netidx]["uvia_drill"] = 0.1
    return nets_info, differential_pairs
    
def extract_nets_indices(pcb: KicadPCB, delete_nets: Optional[Set[str]]=None) -> Set[int]:

    all_net_indices = set([n[0] for n in pcb["net"]])
    module_nets = collections.defaultdict(int)

    for module in pcb.module:
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

def extract_layer(pcb: KicadPCB) -> List[str]:

    layers = list()

    for k in sorted(pcb.layers):
        if "signal" == pcb.layers[k][-1]:
            layers.append(pcb.layers[k][0])

    return layers

def extract_net_pads(pcb: KicadPCB, 
                     layers: List[str], 
                     exclude_nets: List[int],
                     net_indices: Set[int],
                     obs_pad_value: int
                    ) -> Dict[float, List[Any]]:

    net2pads = collections.defaultdict(list)

    for module in pcb.module:
        module_pos = tuple(module.at)
        for p in module.pad:
            pads_info = extract_pad(p, module_pos, layers, net_indices, obs_pad_value)
            for p_info in pads_info:
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
    for pl in module_pad.layers:
        if pl in layers:
            pad_info = {}
            p_rotation = module_pad["at"][2] if len(module_pad["at"])==3 else 0
            pad_info["relative_pos"] = tuple(module_pad["at"])[:2]
            pad_info["size"] = tuple(module_pad["size"])
            pad_info["shape"] = module_pad[2]
            pad_info["m_rotation"] = m_rotation
            pad_info["p_rotation"] = p_rotation - m_rotation
            pad_info["layer"] = pl
            pad_info["module_pos"] = tuple(module_pos)[:2]
            pad_info["drill_hole"] = False
            ret_pads.append([pad_net_idx, pad_info])
        elif pl == "*.Cu":
            for p_layer in layers:
                pad_info = {}
                p_rotation = module_pad["at"][2] if len(module_pad["at"])==3 else 0
                pad_info["relative_pos"] = tuple(module_pad["at"])[:2]
                pad_info["size"] = tuple(module_pad["size"])
                pad_info["shape"] = module_pad[2]
                pad_info["m_rotation"] = m_rotation
                pad_info["p_rotation"] = p_rotation - m_rotation
                pad_info["layer"] = p_layer
                pad_info["module_pos"] = tuple(module_pos)[:2]
                pad_info["drill_hole"] = True
                ret_pads.append([pad_net_idx, pad_info])

    return ret_pads

def extract_bound(
        gr_lines: List[Dict[str, Any]], 
        gr_arcs: List[Dict[str, Any]]
    ) -> Tuple[float, float, float, float, List[Any]]:

    lines = []
    min_x, min_y = float("inf"), float("inf")
    max_x, max_y = float("-inf"), float("-inf") 
    width = 0
    for line in gr_lines:
        if line["layer"][1:-1] == "Edge.Cuts" or line["layer"] == "Edge.Cuts":
            width = line.width if "width" in line else line.stroke.width  # kicad v5 vs v6
            min_x = min([min_x, line.start[0]+width, line.end[0]+width])
            min_y = min([min_y, line.start[1]+width, line.end[1]+width])
            max_x = max([max_x, line.start[0]-width, line.end[0]-width])
            max_y = max([max_y, line.start[1]-width, line.end[1]-width])
            lines.append([tuple(line.start), tuple(line.end), width])
    for arcs in gr_arcs:
        if arcs["layer"][1:-1] == "Edge.Cuts" or arcs["layer"] == "Edge.Cuts":
            width = arcs.width if "width" in arcs else arcs.stroke.width
            min_x = min([min_x, arcs.start[0]+width, arcs.end[0]+width])
            min_y = min([min_y, arcs.start[1]+width, arcs.end[1]+width])
            max_x = max([max_x, arcs.start[0]-width, arcs.end[0]-width])
            max_y = max([max_y, arcs.start[1]-width, arcs.end[1]-width])
            lines.append([tuple(arcs.start), tuple(arcs.end), arcs.angle, width])
    
    return min_x, min_y, max_x, max_y, lines

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


if __name__ == "__main__":
    kicad_filename = "./benchmarks/real_world/1bitsy.kicad_pcb"
    pcb = PCB(kicad_filename)