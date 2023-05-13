from typing import Any, Dict, Iterable, List, Optional, Set, Tuple, Union
import numpy as np
import collections
from .thirdparty.kicad_parser.kicad_pcb import *
from .thirdparty.kicad_parser.sexp_parser import *
import json, re
from .utils.pad_rotation import calculate_pad_pos_size

def extract_recursive(sexp_obj: Sexp, 
                      exclude:list = [], only:list = None, 
                      parents:list = None):
    ret_dict = {}
    if (not isinstance(sexp_obj._value,str)) and \
        (any(isinstance(item,(Sexp)) for item in sexp_obj._value) or (isinstance(sexp_obj._value,OrderedDict))):
        for item in sexp_obj._value:
            if item not in exclude:
                if isinstance(item, Sexp):
                    ret_dict[item._key] = extract_recursive(item, exclude=exclude)
                else:
                    curr_val = sexp_obj[item]
                    ret_dict[item] = curr_val\
                                            if not isinstance(curr_val, Sexp) \
                                            else extract_recursive(curr_val, exclude=exclude) if not isinstance(curr_val, Iterable)\
                                            else [extract_recursive(sub_item) for sub_item in curr_val]           
    else: 
        ret_dict[sexp_obj._key] = sexp_obj._value

    return ret_dict


class PCB:
    def __init__(
            self, 
            kicad_file: str="benchmarks/real_world/1bitsy.kicad_pcb", 
            delete_nets: Optional[Set[str]]=None
        ) -> None:
        self.file = kicad_file
        self.obs_pad_value = -1
        self.via_obs_pad_value = -2
        self.pcb = KicadPCB.load(kicad_file)
        self.max_layer_index = 16 if self.pcb.version == 3 else 32
        self.layers = extract_layer(pcb=self.pcb, max_layer_index=self.max_layer_index)

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

    # def dump_to_PBCRDL_json(self, target_dir):
    #     def repl_func(match: re.Match):
    #         # JSON formatting helper
    #         return " ".join(match.group().split())

    #     dump = {
    #             "layers": self.layers, 
    #             "unit": "mm", # TODO: check where this is defined in kicad files
                
    #             "circuit_region": self.circuit_range,  # this is is region of circuit, expressed by xy coordinates 

    #             # this is a list containing all the boundaries lines
    #             "boundaries": self.boundary_lines,
    #             "net_indices": list(self.net_indices),
    #             'layers':len(self.layers),
    #             'unit': 'mm STATIC',
    #             'nets': self._net_pads,
    #             'rules':{
    #                 'net_classes': extract_net_classes(self.pcb) # TODO: is there a better way than extract_netclasses?
    #             },
    #             'solution': {
    #                 'wires': extract_track_pieces(self._wires),
    #                 'arcs': extract_track_pieces(self.pcb.arc),
    #                 'vias': extract_track_pieces(self._vias)
    #             }
    #         }
    #     with open(f'{target_dir}final.json', 'w') as fd:
    #         s = json.dumps(dump,indent=2)
    #         s = re.sub("(?<=\[)[^\[\]]+(?=])", repl_func, s)
    #         fd.write(s)


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

    for i_m, module in enumerate(pcb.module):
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
        if pl == "*.Cu":
            pad_info["layer"] = layers
            break
        elif pl in layers:
            pad_info["layer"].append(pl)
    pad_info["drill_hole"] = False if pad_info["layer"]==1 else True
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
            lines.append({"type":"polyline", "start":tuple(line.start), "end":tuple(line.end), "width":width})
    for arcs in gr_arcs:
        if arcs["layer"][1:-1] == "Edge.Cuts" or arcs["layer"] == "Edge.Cuts":
            width = arcs.width if "width" in arcs else arcs.stroke.width
            min_x = min([min_x, arcs.start[0]+width, arcs.end[0]+width])
            min_y = min([min_y, arcs.start[1]+width, arcs.end[1]+width])
            max_x = max([max_x, arcs.start[0]-width, arcs.end[0]-width])
            max_y = max([max_y, arcs.start[1]-width, arcs.end[1]-width])
            lines.append({"type":"arc", "start":tuple(arcs.start), "end":tuple(arcs.end), "clockwise_angle": arcs.angle, "width":width})
    
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

def extract_net_classes(pcb: PCB):
    net_classes = [extract_recursive(net_class) for net_class in pcb.net_class]
    name_and_index = [extract_recursive(net) for net in pcb.net]
    nameKey_indexVal = {net['net'][1]:net['net'][0] for net in name_and_index}
    # Loop to deal with kinda silly add net structure of old files.
    for net_class in net_classes:
        nets = []
        net_class['class_name'] = net_class.pop(0)
        net_class['class_desc'] = net_class.pop(1)
        for net in net_class['add_net']:
            nets.append(net['add_net'])
        net_class['indices'] = [nameKey_indexVal[net] for net in nets]
        del net_class['add_net']
    return net_classes
    
def extract_track_pieces(track_list:list):
    pieces = [extract_recursive(piece) for piece in track_list]
    for piece in pieces:
        try:
            del piece['tstamp']
        except KeyError:
            continue
    return pieces

