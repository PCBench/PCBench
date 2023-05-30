from dataclasses import dataclass, field
from typing import Optional, List


@dataclass
class EnvParams:

    pcb_path: str = "../../PCBs/1Bitsy_1bitsy/final.json"
    load_model: Optional[str] = "../RL/models/policy_kitspace_CocoMixtape_UGM_Kicad"
    grid_resolution: float = 0.5

