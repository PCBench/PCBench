import json
from typing import Any, Dict, Tuple, List
from .PCBGrid import PCBGridize
import numpy as np
from collections import defaultdict

def load_json(pcb_file_path: str) -> Dict[str, Any]:
    with open(pcb_file_path) as jf:
        pcb_dict = json.load(jf)
    return pcb_dict


class Rules:
    def __init__(self, wire_width, clearance, via_diameter) -> None:
        self.wire_width = wire_width
        self.clearance = clearance
        self.via_diameter = via_diameter


class PCBState:
    def __init__(
            self,
            nets: Dict[int, List[Tuple[int, int, int]]]=None,
            pad_regions: Dict[Tuple[int, int, int], List[Tuple[int, int, int]]]=None,
            obstacles: List[Tuple[int, int, int]]=None,
            grid_dim: Tuple[int, int, int]=None,
            paths: Dict[int, List[List[Tuple[int, int, int]]]]=None,
            rules: Rules=None, 
            agent_location: Tuple[int, int, int]=None,
            target_location: Tuple[int, int, int]=None
        ) -> None:
        self.nets = nets
        self.pad_regions = pad_regions
        self.obstacles = obstacles
        self.grid_dim = grid_dim
        self.paths = paths if paths is not None else defaultdict(list)
        self.rules = rules
        self.agent_location = agent_location
        self.target_location = target_location 


class PCBLoader:
    def __init__(self, pcb_name: str, resolution: Tuple[float, float]=None) -> None:
        self.pcb_name = pcb_name
        self.resolution = resolution

    def load(self) -> Tuple[np.ndarray, PCBState, List[str]]:

        self.pcb = load_json(self.pcb_name)
        rules = self._load_net_mata_info()

        if self.resolution is None:
            self.resolution = [self.pcb["rules"]["net_classes"][0]["clearance"], self.pcb["rules"]["net_classes"][0]["clearance"]]
        routing_matrix, nets, pad_regions = PCBGridize(self.pcb, self.resolution)

        obstacles = []
        if -1 in nets:
            obs_pads = nets.pop(-1)
            for obs in obs_pads:
                obstacles += pad_regions.pop(obs)

        pcb_state = PCBState(
            nets=nets,
            pad_regions=pad_regions,
            obstacles=obstacles,
            grid_dim=routing_matrix.shape,
            rules=rules
        )
        return routing_matrix, pcb_state, self.pcb["layers"]

    def _load_net_mata_info(self) -> Dict[int, Rules]:
        net_meta_tmp = dict()
        net_classes = self.pcb["rules"]["net_classes"]
        for net_class in net_classes:
            for net_idx in net_class["indices"]:
                net_meta_tmp[net_idx] = Rules(
                    wire_width=net_class["width"],
                    clearance=net_class["clearance"],
                    via_diameter=net_class["via_diameter"]
                )
        return net_meta_tmp
