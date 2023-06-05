from typing import List
from PCBRoutingEnv import PCBRoutingEnv
from scipy.spatial.distance import cityblock
import numpy as np

class VLSIDATEnv(PCBRoutingEnv):
    def __init__(
        self, 
        resolution: float, 
        pcb_folder: str, 
        pcb_names: List[str], 
        connect_coef: float=20.0,
        dist_coef: float=0.5,
        path_coef: float = 0.1
    ) -> None:
        super().__init__(resolution, pcb_folder, pcb_names)
        self.connect_coef = connect_coef
        self.dist_coef = dist_coef
        self.path_coef = path_coef

    def reward(self) -> float:
        if np.array_equal(self._agent_location, self._target_location):
            return self.connect_coef
        if self.conflict:
            return -self.dist_coef * cityblock(self._agent_location, self._target_location)
        
        return -self.path_coef
