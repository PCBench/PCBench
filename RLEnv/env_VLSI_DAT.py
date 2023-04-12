from typing import List
from RLEnv.PCBEnvPos import PCBEnvPos
from scipy.spatial.distance import cityblock

class VLSIDATEnv(PCBEnvPos):
    
    def _get_reward(self) -> float:
        return 10 * self.num_connected_pairs - 20 * cityblock(self._agent_location, self._target_location) - self.path_length