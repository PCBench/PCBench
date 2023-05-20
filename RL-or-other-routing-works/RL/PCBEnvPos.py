import sys
sys.path.append('..')

from typing import List, Tuple
import gymnasium as gym
from gymnasium import spaces
import numpy as np
from load_data.RLoader import PCBLoader
from utils.geometry import closest_point_idx, nodes_inside_rectangle, nodes_inside_circle
from collections import defaultdict
import random
import os
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
        
        self.nets_indices = sorted(list(self.nets.keys()))
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

        next_location = self._clip_position(new_location)
        self._agent_location = next_location

        if tuple(next_location) in self.pad_region[tuple(self._target_location)]:
            self._to_next_pair()
            if self.terminated:
                return
        else:
            wire_intersect = self._is_wire_intersect(
                start=tuple(self.current_path[-1]), 
                end=tuple(next_location)
            )
            if wire_intersect or tuple(next_location) in self.current_path:
                if self.termination_rule == "vr":
                    self._to_next_pair()
                    if self.terminated:
                        return
                self.DRVs += 1
                self.conflict = True
            else:
                self._add_wires(self.current_path[-1], self._agent_location)
        
        if self.termination_rule == "v" and self.DRVs > 0:
            self.terminated = True

    def _is_wire_intersect(self, start: Tuple[int, int, int], end: Tuple[int, int, int]) -> bool:
        curr_net_meta = self.net_meta[self.current_net]
        wire_width = curr_net_meta.wire_width + 2 * curr_net_meta.clearance
        via_width = curr_net_meta.via_diameter + 2 * curr_net_meta.clearance
        if start[-1] == end[-1]:
            inside_nodes = nodes_inside_rectangle(
                start=(start[0], start[1]), 
                end=(end[0], end[1]), 
                width=wire_width, 
                resolution=self.resolution
            )
        else:
            inside_nodes = nodes_inside_circle(
                center=(start[0], start[1]), 
                diameter=via_width, 
                resolution=self.resolution
            )
        for layer in set([start[-1], end[-1]]):
            for node in inside_nodes:
                pos = tuple(self._clip_position(node + (layer,)))
                if self.pcb_matrix[pos] != 0 and self.pcb_matrix[pos] != curr_net_meta.net_index:
                    return True
        return False

    def _add_wires(self, start: np.ndarray, end: np.ndarray) -> None:
        # print(f"add wires?{start}, {end}")
        wire_width = self.net_meta[self.current_net].wire_width
        via_width = self.net_meta[self.current_net].via_diameter
        if start[-1] == end[-1]:
            inside_nodes = nodes_inside_rectangle(
                start=(start[0], start[1]), 
                end=(end[0], end[1]), 
                width=wire_width, 
                resolution=self.resolution
            )
        else:
            inside_nodes = nodes_inside_circle(
                center=(start[0], start[1]), 
                diameter=via_width, 
                resolution=self.resolution
            )
        # print(inside_nodes, wire_width, via_width)
        for layer in set([start[-1], end[-1]]):
            for node in inside_nodes:
                pos = self._clip_position(node + (layer,))
                self.pcb_matrix[tuple(pos)] = self.current_net
                # print(pos, self.pcb_matrix[tuple(pos)])

    def _clip_position(self, position: np.ndarray) -> np.ndarray:
        return np.clip(
                position,
                [0, 0, 0], 
                [self.pcb_matrix.shape[0]-1, self.pcb_matrix.shape[1]-1, self.pcb_matrix.shape[2]-1],
            )

    def _get_reward(self) -> float:
    
        return -self.DRV_penalty_coef * self.DRVs - self.path_length if self.terminated else 0

    def render(self):
        pass

    def _render_frame(self):
        pass

    def close(self):
        pass