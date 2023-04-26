from dataclasses import dataclass, field
from typing import Optional


@dataclass
class EnvParams:

    pcb_path: str = "../../PCBs/1Bitsy_1bitsy_v5/processed.kicad_pcb"
    load_model: Optional[str] = "./rl_model/policy_test"
    grid_resolution: float = 0.5

