import json
from typing import Any, Dict, Tuple
from .PCBGridize import PCBGridize

def load_json(pcb_file_path: str) -> Dict[str, Any]:
    with open(pcb_file_path) as jf:
        pcb_dict = json.load(jf)

    return pcb_dict


class NetMeta:
    def __init__(self, net_index, wire_width, clearance, via_diameter) -> None:
        self.net_index = net_index
        self.wire_width = wire_width
        self.clearance = clearance
        self.via_diameter = via_diameter


class PCBLoader:
    def __init__(self, pcb_name: str, resolution: Tuple[float, float]=None) -> None:
        self.pcb = load_json(pcb_name)
        self._net_meta = self._load_net_mata_info()

        if resolution is None:
            resolution = [self.pcb["rules"]["net_classes"][0]["clearance"], self.pcb["rules"]["net_classes"][0]["clearance"]]
        self._routing_matrix, self._net_pads, self._pad_regions = PCBGridize(self.pcb, resolution)

    @property
    def layers(self):
        return self.pcb["layers"]

    @property
    def net_meta(self):
        return self._net_meta

    @property
    def routing_matrix(self):
        return self._routing_matrix

    @property
    def net_pads(self):
        return self._net_pads

    @property
    def pad_regions(self):
        return self._pad_regions
    
    def _load_net_mata_info(self) -> Dict[int, NetMeta]:
        net_meta_tmp = dict()
        net_classes = self.pcb["rules"]["net_classes"]
        for net_class in net_classes:
            for net_idx in net_class["indices"]:
                net_meta_tmp[net_idx] = NetMeta(
                    net_index=net_idx,
                    wire_width=net_class["width"],
                    clearance=net_class["clearance"],
                    via_diameter=net_class["via_diameter"]
                )
        return net_meta_tmp
