import gymnasium as gym
from gymnasium import spaces
import numpy as np
from ..extract_kicad import PCB
from ..utils import DRC


def act2wire():
    pass

def select_pins():
    pass

def add_wires():
    pass

class PCBaseEnv(gym.Env):
    def __init__(self, pcb: PCB, render_mode: str=None):
        self.pcb = pcb
        self._unrouted_net_indices = sorted(list(pcb.net_indices))
        self._current_net = 0 # index of unrouted net indices
        self.DRC = DRC.DesignRuleChecker()

        # reset?
        self._agent_location = self.pcb.net_pads[self._unrouted_net_indices[self._current_net]][0]["pad_center_xy"]
        self._target_location = self.pcb.net_pads[self._unrouted_net_indices[self._current_net]][1]["pad_center_xy"]

    def _get_obs(self):
        return {"agent": self._agent_location, "target": self._target_location}

    def _get_info(self):
        return {
            "distance": np.linalg.norm(
                self._agent_location - self._target_location, ord=1
            )
        }

    def reset(self, seed=None, options=None):
        pass

    def step(self, action):

        # We use `np.clip` to make sure we don't leave the grid
        self._agent_location = np.clip(
            action, [self.pcb.circuit_range[0], self.pcb.circuit_range[1]], [self.pcb.circuit_range[2], self.pcb.circuit_range[3]]
        )

        # update state
        new_wires = act2wire()
        self.DRC.update(pcb=self.pcb, new_wires=new_wires)
        add_wires()

        # TODO: revise termination
        """
        check if current pin pair is connected, if so, we need to select a new pin pair or go to next net, otherwise do nothing
        """
        terminated = False
        if np.array_equal(self._agent_location, self._target_location):
            pass
        terminated = np.array_equal(self._agent_location, self._target_location)
        reward = -self.DRC.DRV if terminated else 0
        observation = self._get_obs()
        info = self._get_info()

        return observation, reward, terminated, False, info

    def render(self):
        pass

    def _render_frame(self):
        pass

    def close(self):
        pass