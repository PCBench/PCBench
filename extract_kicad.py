from typing import Any, Dict, List, Optional, Set, Tuple
import collections
from thirdparty.kicad_parser.kicad_pcb import *
from thirdparty.kicad_parser.sexp_parser import *

class PCB:
    def __init__(self, kicad_file: str="benchmarks/real_world/1bitsy.kicad_pcb", delete_nets: Optional[Set[str]]=None) -> None:

        self.obs_pad_value = -0.1
        self.via_obs_pad_value = -0.2
        self.pcb = KicadPCB.load(kicad_file)

        self.layers = self.extract_layer()

        # extract boundary info: circuit region and boundary lines with width
        min_x, min_y, max_x, max_y, lines = self.extract_bound(self.pcb.gr_line, self.pcb.gr_arc)
        self.circuit_range = [min_x, min_y, max_x, max_y]
        self.boundary_lines = lines

        # extract net info: net indices, pads with their regions
        self.net_indices = self.extract_nets_indices(delete_nets=delete_nets)
        self.nets = self.extract_nets()

        # extract default wire width and clearance
        try:
            self.segment_width = self.pcb.net_class[0].trace_width
            self.trace_clearance = self.pcb.net_class[0].clearance
            self.via_size = self.pcb.net_class[0].via_dia
        except:
            print(f"there is no default net class, setting clearance manually!!")
            self.segment_width = 0.3
            self.trace_clearance = 0.12
            self.via_size = 0.5

    def extract_nets_indices(self, delete_nets: Optional[Set[str]]=None) -> None:

        all_net_indices = set([n[0] for n in self.pcb["net"]])
        module_nets = collections.defaultdict(int)

        for module in self.pcb.module:
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

    def extract_layer(self) -> List[str]:

        layers = list()

        for k in sorted(self.pcb.layers):
            if "signal" == self.pcb.layers[k][-1]:
                layers.append(self.pcb.layers[k][0])

        return layers

    def extract_nets(self) -> Dict[float, List[Any]]:

        net2pads = collections.defaultdict(list)

        for module in self.pcb.module:
            module_pos = tuple(module.at)
            for p in module.pad:
                pads_info = self.extract_pad(p, module_pos)
                for p_info in pads_info:
                    net2pads[p_info[0]].append(p_info[1])
        
        for via in self.pcb.via:
            pads_info = self.extract_single_via_pad(via)
            for pad_info in pads_info:
                net2pads[self.via_obs_pad_value].append(pad_info[1])

        return net2pads

    def extract_pad(self, module_pad: Dict[str, List[Any]], module_pos: Any) -> List[Any]:

        pad_net_idx = module_pad["net"][0] if "net" in module_pad and module_pad["net"][0] in self.net_indices else self.obs_pad_value
        # pad_shape = module_pad[2]
        m_rotation = module_pos[2] if len(module_pos)==3 else 0

        ret_pads = []   # return 2 pads info if it is a drill hole
        for pl in module_pad.layers:
            if pl in self.layers:
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
                for p_layer in self.layers:
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

    def extract_bound(self, gr_lines: List[Dict[str, Any]], gr_arcs: List[Dict[str, Any]]) -> Tuple[float, float, float, float, List[Any]]:

        lines = []
        min_x, min_y = float("inf"), float("inf")
        max_x, max_y = float("-inf"), float("-inf")    
        for line in gr_lines:
            if line["layer"][1:-1] == "Edge.Cuts" or line["layer"] == "Edge.Cuts":
                width = 0
                min_x = min([min_x, line.start[0]+width, line.end[0]+width])
                min_y = min([min_y, line.start[1]+width, line.end[1]+width])
                max_x = max([max_x, line.start[0]-width, line.end[0]-width])
                max_y = max([max_y, line.start[1]-width, line.end[1]-width])
                lines.append([tuple(line.start), tuple(line.end), line.width])
        for arcs in gr_arcs:
            width = 0
            min_x = min([min_x, arcs.start[0]+width, arcs.end[0]+width])
            min_y = min([min_y, arcs.start[1]+width, arcs.end[1]+width])
            max_x = max([max_x, arcs.start[0]-width, arcs.end[0]-width])
            max_y = max([max_y, arcs.start[1]-width, arcs.end[1]-width])
        
        return min_x, min_y, max_x, max_y, lines

    def extract_single_via_pad(self, via_info: Dict[str, Any]) -> List[Any]:
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