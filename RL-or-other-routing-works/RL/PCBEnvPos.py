import sys
sys.path.append('..')

from typing import List
import gymnasium as gym
from gymnasium import spaces
import numpy as np
from load_data.RLoader import PCBLoader
from load_data.geometry import closest_point_idx
from collections import defaultdict
import random
import os
import json
from copy import deepcopy

class PCBEnvPos(gym.Env):
    def __init__(
            self, 
            resolution: float, 
            pcb_folder: str, 
            pcb_names: List[str], 
            termination_rule: str,
            DRV_penalty_coef: float=10.0
        ) -> None:
        self.resolution = resolution
        self.pcb_names = pcb_names
        self.pcb_folder = pcb_folder
        self.termination_rule = termination_rule
        self.DRV_penalty_coef = DRV_penalty_coef
        n_actions = 6
        self._action_to_direction = {
            0: np.array([1, 0, 0]),
            1: np.array([0, 1, 0]),
            2: np.array([-1, 0, 0]),
            3: np.array([0, -1, 0]),
            4: np.array([0, 0, 1]),
            5: np.array([0, 0, -1])
        }
        self.state_shape = (6,)
        self.action_space = spaces.Discrete(n_actions)
        self.observation_space = spaces.Box(low=0, high=30, shape=self.state_shape, dtype=np.float32)

        self.pcb_holder = {}
    
    def _get_obs(self) -> np.ndarray:
        return np.array(np.concatenate((self._agent_location, self._target_location)))

    def _get_info(self):
        return {
            "distance": np.linalg.norm(
                self._agent_location - self._target_location, ord=1
            )
        }

    def reset(self):

        self.pcb_name = random.choice(self.pcb_names)

        if self.pcb_name in self.pcb_holder:
            pcb = self.pcb_holder[self.pcb_name]
        else:
            pcb_file_path = os.path.join(self.pcb_folder, self.pcb_name + '/final.json')
            pcb = PCBLoader(pcb_file_path, self.resolution)
            self.pcb_holder[self.pcb_name] = pcb

        self.pcb_matrix, self.nets = deepcopy(pcb.routing_matrix), deepcopy(pcb.net_pads)
        self.pad_region = pcb.pad_regions
        self.layers = pcb.layers
        self.net_meta = pcb.net_meta
        
        self.nets_indices = list(self.nets.keys())
        self.current_net = self.nets_indices.pop(0)
        self._agent_location = np.array(self.nets[self.current_net].pop(0))
        self._target_location = np.array(self.nets[self.current_net].pop(closest_point_idx(self._agent_location, self.nets[self.current_net])))
        
        self.path_length = 0
        self.DRVs = 0
        self.num_connected_pairs = 0
        self.nets_path = defaultdict(list)
        self.current_path = [tuple(self._agent_location)]

        self.terminated = False
        self.conflict = False

        return self._get_obs(), self._get_info()

    def step(self, action: int):

        self._update_state(action=action)
        
        reward = self._get_reward()
        observation = self._get_obs()
        info = self._get_info()

        return observation, reward, self.terminated, False, info
    
    def _to_next_pair(self) -> None:

        self.num_connected_pairs += 1
        self.nets_path[self.current_net].append(self.current_path)
        if len(self.nets[self.current_net]) == 0:
            if len(self.nets_indices) == 0:
                self.terminated = True
                return
            else:
                self.current_net = self.nets_indices.pop(0)
                # if len(self.nets[self.current_net]) == 1:
                #     print(f'why does this happen? {self.current_net}')
            self._agent_location = np.array(self.nets[self.current_net].pop(0))
        else:
            self._agent_location = self._target_location

        self._target_location = np.array(self.nets[self.current_net].pop(closest_point_idx(self._agent_location, self.nets[self.current_net])))
        self.current_path = [tuple(self._agent_location)]
        self.path_length += 1

    def _update_state(self, action: int) -> None:

        direction = self._action_to_direction[action]
        new_location = self._agent_location + direction
        self.current_path.append(tuple(self._agent_location))
        self.path_length += 1
        # We use `np.clip` to make sure we don't leave the grid
        self._agent_location = np.clip(
                new_location,
                [0, 0, 0], 
                [self.pcb_matrix.shape[0]-1, self.pcb_matrix.shape[1]-1, len(self.layers)-1],
            )
        matrix_value = self.pcb_matrix[tuple(self._agent_location)]
        # if np.array_equal(new_location, self._target_location):
        if tuple(self._agent_location) in self.pad_region[tuple(self._target_location)]:
            self._to_next_pair()
            if self.terminated:
                return
        else:
            if (matrix_value != 0 and matrix_value != self.current_net) or tuple(new_location) in self.current_path:
                if self.termination_rule == "vr":
                    self._to_next_pair()
                    if self.terminated:
                        return
                self.DRVs += 1
                self.conflict = True
            else:
                # TODO: add wire width
                self.pcb_matrix[tuple(self._agent_location)] = self.current_net
        
        if self.termination_rule == "v" and self.DRVs > 0:
            self.terminated = True

    def _get_reward(self) -> float:
    
        return -self.DRV_penalty_coef * self.DRVs - self.path_length if self.terminated else 0

    def render(self):
        pass

    def _render_frame(self):
        pass

    def close(self):
        pass