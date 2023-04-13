from typing import List
from RLEnv.PCBEnvPos import PCBEnvPos
from scipy.spatial.distance import cityblock

class VLSIDATEnv(PCBEnvPos):
    def __init__(
        self, 
        resolution: float, 
        pcb_folder: str, 
        pcb_names: List[str], 
        termination_rule: str,
        DRV_penalty_coef: float=10.0,
        connect_coef: float=10.0,
        dist_coef: float=20.0,
        path_coef: float = 1.0
    ) -> None:
        super().__init__(resolution, pcb_folder, pcb_names, termination_rule, DRV_penalty_coef)
        self.connect_coef = connect_coef
        self.dist_coef = dist_coef
        self.path_coef = path_coef
                
    def _get_reward(self) -> float:
        return self.connect_coef * self.num_connected_pairs - \
               self.dist_coef * cityblock(self._agent_location, self._target_location) - \
               self.path_coef * self.path_length